import React, { useEffect, useState } from 'react';
import './Home.css';
import PhotoSlider from '../PhotoSlider/PhotoSlider';
import { sendPhotoId, uploadFile } from '../../api';
import Header from '../Header/Header';
const Home = () => {
  const [file, setFile] = useState(null);
  const [error, setError] = useState('');
  const [uuid, setUuid] = useState(localStorage.getItem('uuid') || '');
  const [numSlices, setNumSlices] = useState(localStorage.getItem('numSlices') || '');
  const [photo, setPhoto] = useState(0);
  const [isSending, setIsSending] = useState(false);
  const [isSending1, setIsSending1] = useState(false);
  const [isUploaded, setIsUploaded] = useState(false);
  const [resultImage, setResultImage] = useState(null);
  const [isChoosed, setIsChoosed] = useState(false);
  const [imageSettings, setImageSettings] = useState(false);

  useEffect(() => {
    const cachedImages = JSON.parse(localStorage.getItem('cachedImages') || '{}');
    if (cachedImages[uuid]?.[photo] && isChoosed === true) {
      setResultImage(cachedImages[uuid][photo]);
    }
  }, [uuid, photo]);

  useEffect(() => {
    return () => {
      if (resultImage) {
        URL.revokeObjectURL(resultImage);
      }
    };
  }, [resultImage]);

  const cacheImage = async (uuid, sliceNum, blob) => {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64data = reader.result;
        const cachedImages = JSON.parse(localStorage.getItem('cachedImages') || '{}');

        if (!cachedImages[uuid]) {
          cachedImages[uuid] = {};
        }

        cachedImages[uuid][sliceNum] = base64data;
        localStorage.setItem('cachedImages', JSON.stringify(cachedImages));
        resolve(base64data);
      };
      reader.readAsDataURL(blob);
    });
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];

    if (selectedFile) {
      if (selectedFile.name.endsWith('.nii')) {
        setFile(selectedFile);
        setError('');
        setIsChoosed(true);
      } else {
        setFile(null);
        setError('Загрузить можно только .nii файл!');
      }
    }
  };

  const handleUpload = async () => {
    try {
      setIsSending1(true);
      const response = await uploadFile(file);

      const { uuid, num_slices } = response;
      setUuid(uuid);
      setNumSlices(num_slices);

      localStorage.setItem('uuid', uuid);
      localStorage.setItem('numSlices', num_slices);
      setIsUploaded(true);
      setResultImage(null);
    } catch (error) {
      console.log('error', error);
      setIsUploaded(false);
    } finally {
      setIsSending1(false);
    }
  };

  const handleSendSlice = async () => {
    try {
      setIsSending(true);
      setIsSending(true);

      const cachedImages = JSON.parse(localStorage.getItem('cachedImages') || '{}');
      if (cachedImages[uuid]?.[photo]) {
        setResultImage(cachedImages[uuid][photo]);
        return;
      }

      const blob = await sendPhotoId(uuid, photo);

      const blobUrl = URL.createObjectURL(blob);
      setResultImage(blobUrl);
      await cacheImage(uuid, photo, blob);
    } catch (error) {
      console.error('error while sending id', error);
    } finally {
      setIsSending(false);
    }
  };

  const clickedImage = () => {
    setImageSettings((prev) => !prev);
  };

  return (
    <div className="Home">
      <Header />
      <div className="file-upload-section">
        <div className="file-input-wrapper">
          <input
            type="file"
            id="button-choose"
            accept=".nii"
            onChange={handleFileChange}
            className="hidden-input"
          />
          <label
            htmlFor="button-choose"
            className="file-choose-button"
          >
            Выбрать файл
          </label>

          {isChoosed && (
            <div className="file-info">
              <span className="file-name">Файл: {file?.name}</span>
              <button
                onClick={handleUpload}
                disabled={!file || isSending1}
                className="upload-button"
              >
                {isSending1 ? (
                  <span>Отправка...</span>
                ) : (
                  <>
                    <img
                      src={'/download.png'}
                      className="upload-icon"
                      width={'16px'}
                      height={'16px'}
                      alt=""
                    />
                    <span>Загрузить</span>
                  </>
                )}
              </button>
            </div>
          )}
        </div>

        {error && <p className="upload-err-msg">{error}</p>}
      </div>

      {isUploaded && (
        <div className="slice-controls">
          <div className="current-count">
            <p>{photo}</p>
          </div>
          <PhotoSlider
            photo={photo}
            setPhoto={setPhoto}
            numSlices={numSlices}
          />
          <div className="slice-count">
            <div className="slider-value start-count">0</div>
            <div className="slider-value end-count">{numSlices}</div>
          </div>
        </div>
      )}

      {isUploaded && (
        <div className="slice-actions">
          <button
            onClick={handleSendSlice}
            disabled={!uuid || isSending || !isUploaded}
            className="get-slice-button"
          >
            {isSending ? 'Отправка...' : 'Получить снимок'}
          </button>
        </div>
      )}
      <div className="container-photo">
        {resultImage && (
          <div className="result-img-container">
            <img
              src={resultImage}
              alt={`Срез ${photo}`}
              className="result-sliced-img"
              onClick={clickedImage}
              draggable="false"
            />
            {imageSettings && (
              <div className='settings-buttons'>
                <button className="settings-button download">Скачать</button>
                <button className="settings-button save">Сохранить в личном кабинете</button>
                <button className="settings-button change">Изменить контур</button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Home;
