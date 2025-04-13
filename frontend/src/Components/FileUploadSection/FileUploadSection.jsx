const FileUploadSection = ({ onFileChange, onUpload, file, error, isUploading }) => (
  <div className="file-upload-section">
    <div className="file-input-wrapper">
      <input
        type="file"
        id="button-choose"
        accept=".nii"
        onChange={onFileChange}
        className="hidden-input"
      />
      <label
        htmlFor="button-choose"
        className="file-choose-button"
      >
        Выбрать файл
      </label>

      {file && (
        <div className="file-info">
          <span className="file-name">Файл: {file.name}</span>
          <button
            onClick={onUpload}
            disabled={!file || isUploading}
            className="upload-button"
          >
            {isUploading ? (
              <span>Отправка...</span>
            ) : (
              <>
                <img
                  src="/download.png"
                  className="upload-icon"
                  width="16px"
                  height="16px"
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
);

export default FileUploadSection;