import React from 'react';
import Slider from 'rc-slider';
import 'rc-slider/assets/index.css';
import './PhotoSlider.css';

const PhotoSlider = ({ photo, setPhoto, numSlices }) => {

  return (
    <>
      <div className="current-count">
        <p>{photo}</p>
      </div>
      <div className="slider">
        <Slider
          value={photo}
          onChange={setPhoto}
          max={numSlices}
          step={1}
          ariaValueTextFormatterForHandle={(val) => `${val}`}
        />
      </div>
    </>
  );
};

export default PhotoSlider;
