# import io
# import cv2
# import torch
# import numpy as np
# import nibabel as nib
# import segmentation_models_pytorch as smp
# import albumentations as A
# from albumentations.pytorch import ToTensorV2
# import matplotlib.pyplot as plt
# from io import BytesIO
#
#
# class ModelSegmentationManager:
#
#     def __init__(self):
#         # Определение параметров модели
#         self.n_cls = 1
#         self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#         # Преобразования для входного изображения
#         self.trans = A.Compose([A.Resize(256, 256), ToTensorV2()])
#         self.model = None
#
#     def upload_model(self):
#         self.model = self.__load_model()
#
#     def __load_model(self):
#         model = smp.DeepLabV3Plus(classes=self.n_cls, in_channels=1)
#         model.load_state_dict(torch.load('model.pth', map_location=self.device))
#         model.to(self.device)
#         model.eval()
#         return model
#
#     @staticmethod
#     def preprocess_im(im):
#         max_val = np.max(im)
#         im[im < 0] = 0
#         return im / max_val
#
#     @staticmethod
#     def read_nii(file_bytes):
#         file_stream = io.BytesIO(file_bytes)
#         try:
#             file_holder = nib.FileHolder(fileobj=file_stream)  # Передаём в FileHolder
#             nii_image = nib.Nifti1Image.from_file_map({'header': file_holder, 'image': file_holder})
#             return nii_image.get_fdata().astype('float32')
#         except Exception as e:
#             print(e)
#
#     def __apply_transformations(self, im):
#         transformed = self.trans(image=im)
#         return transformed["image"].unsqueeze(0).float()
#
#     @staticmethod
#     def __find_contours(mask):
#         mask = mask.squeeze(0)
#         if isinstance(mask, torch.Tensor):
#             mask = mask.cpu().numpy()
#
#         mask = (mask > 0).astype(np.uint8) * 255
#
#         contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#         contour_mask = np.zeros_like(mask)
#
#         cv2.drawContours(contour_mask, contours, -1, (255), thickness=1)
#         return contour_mask
#
#     @staticmethod
#     def __display_results(image, liver_contour):
#         fig, ax = plt.subplots(figsize=(image.shape[2] / 100, image.shape[1] / 100), dpi=100)
#
#         # Убираем оси и рамки
#         ax.axis("off")
#         ax.set_xticks([])
#         ax.set_yticks([])
#         ax.set_frame_on(False)
#
#         # Отображаем изображение
#         ax.imshow(image.squeeze(0).cpu().numpy(), cmap="gray")
#
#         # Добавляем контур
#         ax.contour(liver_contour, colors="r", linewidths=0.8)
#
#         # Сохраняем изображение в буфер
#         buf = BytesIO()
#         plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0, transparent=True)
#         plt.close(fig)
#         buf.seek(0)
#
#         # @staticmethod
#         # def __display_results(image, liver_contour):
#         #     fig, ax = plt.subplots()
#         #     ax.imshow(image.squeeze(0).cpu().numpy(), cmap='gray')
#         #     ax.contour(liver_contour, colors='r', linewidths=0.5)
#         #     buf = BytesIO()
#         #     plt.savefig(buf, format='png')
#         #     plt.close(fig)
#         #     buf.seek(0)
#         #     return buf.getvalue()
#
#         return buf.getvalue()
#
#     def get_result(self, image_volume, num_images):
#
#         image = image_volume[:, :, num_images]
#         image = self.__apply_transformations(image)
#         with torch.no_grad():
#             y_pred = self.model(image)
#         y_pred = torch.sigmoid(y_pred) > 0.5
#
#         contour = self.__find_contours(y_pred[0])
#         result_img = self.__display_results(image[0], contour)
#         return result_img
#
#
# modelManager = ModelSegmentationManager()

import io
import cv2
import torch
import numpy as np
import nibabel as nib
import segmentation_models_pytorch as smp
import albumentations as A
from albumentations.pytorch import ToTensorV2
import matplotlib.pyplot as plt
from io import BytesIO


class ModelSegmentationManager:

    def __init__(self):
        self.n_cls = 1
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Преобразования для входного изображения
        self.trans = A.Compose([A.Resize(256, 256), ToTensorV2()])
        self.model = None

    def upload_model(self):
        self.model = self.__load_model()

    def __load_model(self):
        model = smp.DeepLabV3Plus(classes=self.n_cls, in_channels=1)
        model.load_state_dict(torch.load('model.pth', map_location=self.device))
        model.to(self.device)
        model.eval()
        return model

    @staticmethod
    def preprocess_im(im):
        im = np.clip(im, 0, None)  # Убираем все отрицательные значения
        max_val = np.max(im) or 1  # Защита от деления на 0
        return im / max_val

    @staticmethod
    def read_nii(file_bytes):
        file_stream = io.BytesIO(file_bytes)
        try:
            file_holder = nib.FileHolder(fileobj=file_stream)
            nii_image = nib.Nifti1Image.from_file_map({'header': file_holder, 'image': file_holder})
            return nii_image.get_fdata().astype('float32')
        except Exception as e:
            print(f"Error reading NIfTI file: {e}")
            return None

    def __apply_transformations(self, im):
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

        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0, transparent=True)
        plt.close(fig)
        buf.seek(0)

        return buf.getvalue()

    def get_result(self, image_volume, num_images):
        image = image_volume[:, :, num_images]
        image = self.__apply_transformations(image)

        with torch.no_grad():
            y_pred = torch.sigmoid(self.model(image)) > 0.5  # Прямо в одном вызове

        contour = self.__find_contours(y_pred[0])
        result_img = self.__display_results(image[0], contour)

        return result_img


modelManager = ModelSegmentationManager()
