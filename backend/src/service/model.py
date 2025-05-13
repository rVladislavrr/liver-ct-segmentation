import io
import time

import cv2
import torch
import numpy as np
import nibabel as nib
import segmentation_models_pytorch as smp
import albumentations as A
from albumentations.pytorch import ToTensorV2
import matplotlib.pyplot as plt
from skimage import measure


class ModelSegmentationManager:

    def __init__(self):
        self.n_cls = 1
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Преобразования для входного изображения
        self.trans = A.Compose([A.Resize(256, 256), ToTensorV2()])
        self.model = None

    def upload_model(self):
        self.model = self.__load_model()
        print('✅ Successfully upload model')

    def __load_model(self):
        model = smp.DeepLabV3Plus(classes=self.n_cls, in_channels=1)
        try:
            model.load_state_dict(torch.load('model.pth', map_location=self.device))
        except FileNotFoundError:
            raise RuntimeError("Model file not found")
        model.to(self.device)
        model.eval()
        return model

    @staticmethod
    def __postprocess_mask(mask: torch.Tensor) -> torch.Tensor:
        """Удаляет шумы из бинарной маски с помощью морфологических операций."""
        mask_np = mask.squeeze(0).cpu().numpy().astype(np.uint8) * 255

        # Удаляем мелкие шумы (открытие)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask_np = cv2.morphologyEx(mask_np, cv2.MORPH_OPEN, kernel)

        # Заполняем мелкие дыры (закрытие)
        mask_np = cv2.morphologyEx(mask_np, cv2.MORPH_CLOSE, kernel)

        return torch.from_numpy(mask_np / 255).unsqueeze(0).to(mask.device)

    @staticmethod
    def preprocess_im(im):
        if torch.is_tensor(im):
            im = im.detach().cpu().numpy()
        im = np.clip(im, 0, None)
        max_val = np.max(im) or 1
        return im / max_val

    @staticmethod
    def read_nii(file_bytes):

        file_stream = io.BytesIO(file_bytes)
        file_holder = nib.FileHolder(fileobj=file_stream)
        nii_image = nib.Nifti1Image.from_file_map({'header': file_holder, 'image': file_holder})

        return nii_image.get_fdata().astype('float32')

    def apply_transformations(self, im):
        transformed = self.trans(image=im)
        return transformed["image"].unsqueeze(0).to(self.device, dtype=torch.float32)  # Сразу отправляем на GPU

    @staticmethod
    def __find_contours(mask):
        mask = mask.squeeze(0).cpu().numpy().astype(np.uint8) * 255  # CPU + бинаризация
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        contour_mask = np.zeros_like(mask)
        if contours:
            cv2.drawContours(contour_mask, contours, -1, 255, thickness=1)

        return contour_mask

    @staticmethod
    def __display_results(image, liver_contour):
        image_np = image.squeeze(0).cpu().numpy()  # Переводим в numpy заранее
        fig, ax = plt.subplots(figsize=(image_np.shape[1] / 100, image_np.shape[0] / 100), dpi=100)

        ax.axis("off")
        ax.imshow(image_np, cmap="gray")
        ax.contour(liver_contour, colors="r", linewidths=0.8)

        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0, transparent=True)
        plt.close(fig)
        buf.seek(0)

        return buf.getvalue()

    def __draw_with_user_contours(self, image_slice, user_contours):
        """
        Рисует изображение с множеством пользовательских контуров.
        :param image_slice: NumPy-массив одного среза (H x W)
        :param user_contours: Список контуров [[ [x, y], [x2, y2], ... ], [ ... ], ...]
        :return: PNG-картинка как bytes
        """

        # Удаляем лишнюю размерность, если есть
        if image_slice.ndim == 3 and image_slice.shape[0] == 1:
            image_slice = image_slice.squeeze(0)

        if image_slice.ndim != 2:
            raise ValueError(f"Expected 2D image slice, got shape {image_slice.shape}")

        image_norm = self.preprocess_im(image_slice)
        image_np = (image_norm * 255).astype(np.uint8)

        mask_shape = image_np.shape
        contour_mask = np.zeros((mask_shape[0], mask_shape[1], 3), dtype=np.uint8)

        for contour in user_contours:
            if len(contour) < 2:
                continue
            points = np.array(contour, dtype=np.int32).reshape((-1, 1, 2))
            cv2.polylines(contour_mask, [points], isClosed=True, color=(255, 0, 0), thickness=1)

        image_color = cv2.cvtColor(image_np, cv2.COLOR_GRAY2BGR)
        combined = cv2.addWeighted(image_color, 1.0, contour_mask, 1.0, 0)

        fig, ax = plt.subplots(figsize=(combined.shape[1] / 100, combined.shape[0] / 100), dpi=100)
        ax.axis("off")
        ax.imshow(combined)

        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0, transparent=True)
        plt.close(fig)
        buf.seek(0)

        return buf.getvalue()

    def pred_image(self, image_volume, num_images):
        image = image_volume[:, :, num_images]
        image = self.apply_transformations(image)
        return image

    def get_result_contours(self, image):
        with torch.no_grad():
            y_pred = torch.sigmoid(self.model(image)) > 0.7
        contour = self.__find_contours(y_pred[0])
        contours = measure.find_contours(contour, level=0.7)
        mass_check = set()
        contours_list = []
        for contour in contours:
            new_counter = []
            for point in contour:
                tupl = (round(point[1], 1), round(point[0], 1))
                if tupl not in mass_check:
                    mass_check.add(tupl)
                    new_counter.append(list(tupl))
            contours_list.append(new_counter)

        # contours_list = [[[int(point[1]), int(point[0])] for point in contour] for contour in contours]
        return contours_list

    def create_photo_with_contours(self, image, contours_list):
        result_img = self.__draw_with_user_contours(image[0], contours_list)
        return result_img

    def get_result(self, image_volume, num_images):
        time_start1 = time.time()
        image = image_volume[:, :, num_images]
        image = self.apply_transformations(image)

        with torch.no_grad():
            y_pred = torch.sigmoid(self.model(image)) > 0.7  # 0.5
            # y_pred = self.__postprocess_mask(y_pred)  # Очищаем маску  # Прямо в одном вызове

        contour = self.__find_contours(y_pred[0])
        print(time.time() - time_start1)

        def mask_to_contour(mask: np.ndarray):
            contours = measure.find_contours(mask, level=0.7)
            # Переводим в формат [[x, y], [x, y], ...]
            contours_list = [[[int(point[1]), int(point[0])] for point in contour] for contour in contours]
            return contours_list

        new_contour = mask_to_contour(contour)
        time_start = time.time()
        result_img = self.__display_results(image[0], contour)
        result_img = self.__draw_with_user_contours(image[0], new_contour)
        print(time.time() - time_start)

        return result_img, new_contour

    @staticmethod
    def get_photo(image):
        image_np = image[0].squeeze(0).cpu().numpy()
        fig, ax = plt.subplots(figsize=(image_np.shape[1] / 100, image_np.shape[0] / 100), dpi=100)

        ax.axis("off")
        ax.imshow(image_np, cmap="gray")

        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0, transparent=True)
        plt.close(fig)
        buf.seek(0)
        return buf.getvalue()


modelManager = ModelSegmentationManager()
