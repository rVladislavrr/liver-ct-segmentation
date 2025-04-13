const useImageCache = () => {
  const cacheImage = async (uuid, sliceNum, blob) => {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64data = reader.result;
        const cachedImages = JSON.parse(localStorage.getItem('cachedImages') || '{}');

        if (!cachedImages[uuid]) cachedImages[uuid] = {};
        cachedImages[uuid][sliceNum] = base64data;
        localStorage.setItem('cachedImages', JSON.stringify(cachedImages));
        resolve(base64data);
      };
      reader.readAsDataURL(blob);
    });
  };

  const getCachedImage = (uuid, sliceNum) => {
    const cachedImages = JSON.parse(localStorage.getItem('cachedImages') || '{}');
    return cachedImages[uuid]?.[sliceNum] || null;
  };

  return { cacheImage, getCachedImage };
};

export default useImageCache;