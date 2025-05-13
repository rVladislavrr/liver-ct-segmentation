import React, { useState, useEffect, useRef } from 'react';
import { Stage, Layer, Circle, Image as KonvaImage, Group } from 'react-konva';
import Modal from 'react-modal';
import { getCleanSlice, getContourPoints, saveContourPoints } from '../../api/commonApi';
import './ContourEditorModal.css';

Modal.setAppElement(document.getElementById('root'));

const ContourEditorModal = ({ uuid, sliceIndex, isOpen, onClose, onSave }) => {
  const [points, setPoints] = useState([]);
  const [cleanImage, setCleanImage] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [zoom, setZoom] = useState(1);
  const [isDraggingStage, setIsDraggingStage] = useState(false);
  const [stagePosition, setStagePosition] = useState({ x: 0, y: 0 });
  const stageRef = useRef(null);
  const [lastMousePos, setLastMousePos] = useState({ x: 0, y: 0 });

  const targetWidth = 600;
  const targetHeight = 600;
  const imageWidth = 500;
  const imageHeight = 500;

  const manualScaleX = 1.97;
  const manualScaleY = 1.94;

  useEffect(() => {
    if (!isOpen) return;

    const loadData = async () => {
      setIsLoading(true);
      try {
        const [imageBlob, contourData] = await Promise.all([getCleanSlice(uuid, sliceIndex), getContourPoints(uuid, sliceIndex)]);

        const img = new window.Image();
        img.src = URL.createObjectURL(imageBlob);
        img.onload = () => {
          setCleanImage(img);

          if (contourData && Array.isArray(contourData)) {
            const allPoints = contourData.flat().map(([x, y]) => [Number(x), Number(y)]);
            setPoints(allPoints);
          } else {
            setPoints([]);
          }

          setIsLoading(false);
        };
      } catch (error) {
        console.error('Loading error:', error);
        setIsLoading(false);
      }
    };

    loadData();

    return () => {
      if (cleanImage) URL.revokeObjectURL(cleanImage.src);
    }; // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, uuid, sliceIndex]);

  useEffect(() => {
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    }; // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e) => {
      if (e.code === 'Space') {
        e.preventDefault();
        const stage = stageRef.current;
        const pointerPos = stage.getPointerPosition();
        if (!pointerPos) return;

        const stageX = stage.x();
        const stageY = stage.y();

        const newPoint = [(pointerPos.x - stageX) / zoom / manualScaleX, (pointerPos.y - stageY) / zoom / manualScaleY];

        setPoints([...points, newPoint]);
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, points, zoom]);

  const handlePointDrag = (pointIndex, e) => {
    if (e.evt.button !== 0) return;
    const stage = stageRef.current;
    const stageX = stage.x();
    const stageY = stage.y();

    const newPoints = [...points];
    newPoints[pointIndex] = [stageX, stageY];
    setPoints(newPoints);
  };

  const handlePointClick = (pointIndex, e) => {
    if (e.evt.button === 2) {
      // ПКМ
      e.evt.preventDefault();
      const newPoints = [...points];
      newPoints.splice(pointIndex, 1);
      setPoints(newPoints);
    }
  };

  const handleSave = async () => {
    try {
      await saveContourPoints(uuid, sliceIndex, points);
      onSave();
      onClose();
    } catch (error) {
      console.error('Save error:', error);
    }
  };

  const handleZoomIn = () => {
    setZoom((prev) => {
      const newZoom = Math.min(prev * 1.2, 5);
      setStagePosition({
        x: stagePosition.x * (newZoom / prev),
        y: stagePosition.y * (newZoom / prev),
      });
      return newZoom;
    });
  };

  const handleZoomOut = () => {
    setZoom((prev) => {
      const newZoom = Math.max(prev / 1.2, 0.5);
      setStagePosition({
        x: stagePosition.x * (newZoom / prev),
        y: stagePosition.y * (newZoom / prev),
      });
      return newZoom;
    });
  };

  const handleMouseMove = (e) => {
    if (!isDraggingStage) return;
    setStagePosition((prev) => ({
      x: prev.x + e.movementX,
      y: prev.y + e.movementY,
    }));
  };

  const handleMouseUp = () => {
    setIsDraggingStage(false);
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
  };

  return (
    <Modal
      isOpen={isOpen}
      onRequestClose={onClose}
      className="contour-modal"
      overlayClassName="contour-modal-overlay"
    >
      <div className="modal-content">
        <div className="modal-header">
          <p className="modal-header-title">Редактирование контура</p>
          <button
            onClick={onClose}
            className="close-button"
          >
            &times;
          </button>
        </div>

        <div className="editor-container">
          {isLoading ? (
            <div className="loading-indicator">Загрузка...</div>
          ) : (
            <>
              <div className="size-buttons">
                <p className="hint-text">
                  <b>Колёсико (зажать)</b> — двигать фото
                </p>
                <p className="hint-text">
                  <b>Пробел</b> — добавить точку
                </p>
                <p className="hint-text">
                  <b>ПКМ</b> — удалить точку
                </p>
                <button
                  className="zoom-btn"
                  onClick={handleZoomIn}
                >
                  Увеличить (+)
                </button>
                <button
                  className="zoom-btn"
                  onClick={handleZoomOut}
                  style={{ marginLeft: '10px' }}
                >
                  Уменьшить (-)
                </button>
              </div>

              <Stage
                width={targetWidth + 70}
                height={targetHeight - 40}
                x={stagePosition.x}
                y={stagePosition.y}
                draggable={false}
                onMouseDown={(e) => {
                  if (e.evt.button === 1) {
                    e.evt.preventDefault();
                    setIsDraggingStage(true);
                    setLastMousePos({
                      x: e.evt.clientX,
                      y: e.evt.clientY,
                    });
                  }
                }}
                onMouseMove={(e) => {
                  if (isDraggingStage) {
                    e.evt.preventDefault();
                    const dx = e.evt.clientX - lastMousePos.x;
                    const dy = e.evt.clientY - lastMousePos.y;

                    setStagePosition((prev) => ({
                      x: prev.x + dx,
                      y: prev.y + dy,
                    }));

                    setLastMousePos({
                      x: e.evt.clientX,
                      y: e.evt.clientY,
                    });
                  }
                }}
                onMouseUp={() => {
                  setIsDraggingStage(false);
                }}
                onMouseLeave={() => {
                  setIsDraggingStage(false);
                }}
                onContextMenu={(e) => e.evt.preventDefault()}
                ref={stageRef}
              >
                <Layer>
                  <Group
                    scaleX={zoom}
                    scaleY={zoom}
                  >
                    {cleanImage && (
                      <KonvaImage
                        image={cleanImage}
                        width={imageWidth}
                        height={imageHeight}
                      />
                    )}
                  </Group>

                  <Group
                    scaleX={zoom}
                    scaleY={zoom}
                  >
                    {points.map(([x, y], pointIndex) => (
                      <Circle
                        key={pointIndex}
                        x={x * manualScaleX}
                        y={y * manualScaleY}
                        radius={1}
                        fill="red"
                        draggable
                        onDragMove={(e) => handlePointDrag(pointIndex, e)}
                        onMouseDown={(e) => handlePointClick(pointIndex, e)}
                      />
                    ))}
                  </Group>
                </Layer>
              </Stage>
            </>
          )}
        </div>

        <div className="modal-actions">
          <button
            onClick={onClose}
            className="cancel-button"
          >
            Отмена
          </button>
          <button
            onClick={handleSave}
            disabled={isLoading}
            className="save-button"
          >
            Сохранить
          </button>
        </div>
      </div>
    </Modal>
  );
};

export default ContourEditorModal;
