import React, { useEffect, useState } from 'react';
import './Home.css';
import PhotoSlider from '../PhotoSlider/PhotoSlider';
import { sendPhotoId, uploadFile } from '../../api';
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

  useEffect(() => {
    return () => {
      if (resultImage) {
        URL.revokeObjectURL(resultImage);
      }
    };
  }, [resultImage]);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];

    if (selectedFile) {
      if (selectedFile.name.endsWith('.nii')) {
        setFile(selectedFile);
        setError('');
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

      if (resultImage) {
        URL.revokeObjectURL(resultImage);
        setResultImage(null);
      }
      
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
      const blob = await await sendPhotoId(uuid, photo);
      const imageUrl = URL.createObjectURL(blob);
      if (resultImage) {
        URL.revokeObjectURL(resultImage);
      }
      setResultImage(imageUrl);
    } catch (error) {
      console.error('error while sending id', error);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <>
      <div>
        <input
          type="file"
          accept=".nii"
          onChange={handleFileChange}
        />
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <button
          disabled={!file || isSending1}
          onClick={handleUpload}
        >
          {isSending1 ? 'Отправка...' : 'Загрузить'}
        </button>
      </div>
      {isUploaded && (
        <>
          <PhotoSlider
            photo={photo}
            setPhoto={setPhoto}
            numSlices={numSlices}
          />
          <div className="count">
            <div className="start-count">0</div>
            <div className="end-count">{numSlices}</div>
          </div>
        </>
      )}
      <div>
        <button
          onClick={handleSendSlice}
          disabled={!uuid || isSending || !isUploaded}
        >
          {isSending ? 'Отправка...' : 'Получить снимок'}
        </button>
      </div>

      {resultImage && (
        <div>
          <img
            src={resultImage}
            alt="Фото разреза"
          />
        </div>
      )}
    </>
  );
};

export default Home;
