'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { cn } from '@/lib/utils';

interface ResizablePanelsProps {
  children: [React.ReactNode, React.ReactNode] | [React.ReactNode, React.ReactNode, React.ReactNode];
  orientation?: 'horizontal' | 'vertical';
  defaultSizes?: number[];
  minSizes?: number[];
  maxSizes?: number[];
  className?: string;
  onResize?: (sizes: number[]) => void;
}

interface ResizeHandleProps {
  orientation: 'horizontal' | 'vertical';
  isResizing: boolean;
  onMouseDown: (e: React.MouseEvent) => void;
}

const ResizeHandle: React.FC<ResizeHandleProps> = ({ 
  orientation, 
  isResizing, 
  onMouseDown 
}) => (
  <div
    className={cn(
      "group relative bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 transition-colors cursor-col-resize",
      orientation === 'horizontal' && "w-1 cursor-col-resize",
      orientation === 'vertical' && "h-1 cursor-row-resize",
      isResizing && "bg-blue-500"
    )}
    onMouseDown={onMouseDown}
  >
    <div className={cn(
      "absolute inset-0 flex items-center justify-center",
      orientation === 'horizontal' && "hover:w-2 -mx-0.5",
      orientation === 'vertical' && "hover:h-2 -my-0.5"
    )}>
      <div className={cn(
        "bg-gray-400 dark:bg-gray-500 rounded-full opacity-0 group-hover:opacity-100 transition-opacity",
        orientation === 'horizontal' && "w-1 h-8",
        orientation === 'vertical' && "w-8 h-1"
      )} />
    </div>
  </div>
);

export const ResizablePanels: React.FC<ResizablePanelsProps> = ({
  children,
  orientation = 'horizontal',
  defaultSizes,
  minSizes,
  maxSizes,
  className = '',
  onResize
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isResizing, setIsResizing] = useState(false);
  const [resizingIndex, setResizingIndex] = useState<number | null>(null);
  
  const numPanels = React.Children.count(children);
  const defaultSizePerPanel = 100 / numPanels;
  
  const [sizes, setSizes] = useState<number[]>(
    defaultSizes || Array(numPanels).fill(defaultSizePerPanel)
  );

  const startResize = useCallback((e: React.MouseEvent, index: number) => {
    e.preventDefault();
    setIsResizing(true);
    setResizingIndex(index);
    
    const container = containerRef.current;
    if (!container) return;

    const containerRect = container.getBoundingClientRect();
    const startPos = orientation === 'horizontal' ? e.clientX : e.clientY;
    const containerSize = orientation === 'horizontal' ? containerRect.width : containerRect.height;

    const handleMouseMove = (e: MouseEvent) => {
      const currentPos = orientation === 'horizontal' ? e.clientX : e.clientY;
      const delta = currentPos - startPos;
      const deltaPercent = (delta / containerSize) * 100;

      setSizes(prevSizes => {
        const newSizes = [...prevSizes];
        const minSize1 = minSizes?.[index] || 10;
        const maxSize1 = maxSizes?.[index] || 90;
        const minSize2 = minSizes?.[index + 1] || 10;
        const maxSize2 = maxSizes?.[index + 1] || 90;

        // Calculate new sizes
        let newSize1 = Math.max(minSize1, Math.min(maxSize1, prevSizes[index] + deltaPercent));
        let newSize2 = Math.max(minSize2, Math.min(maxSize2, prevSizes[index + 1] - deltaPercent));

        // Ensure sizes don't exceed bounds
        if (newSize1 < minSize1) {
          newSize1 = minSize1;
          newSize2 = prevSizes[index] + prevSizes[index + 1] - newSize1;
        } else if (newSize1 > maxSize1) {
          newSize1 = maxSize1;
          newSize2 = prevSizes[index] + prevSizes[index + 1] - newSize1;
        }

        if (newSize2 < minSize2) {
          newSize2 = minSize2;
          newSize1 = prevSizes[index] + prevSizes[index + 1] - newSize2;
        } else if (newSize2 > maxSize2) {
          newSize2 = maxSize2;
          newSize1 = prevSizes[index] + prevSizes[index + 1] - newSize2;
        }

        newSizes[index] = newSize1;
        newSizes[index + 1] = newSize2;

        return newSizes;
      });
    };

    const handleMouseUp = () => {
      setIsResizing(false);
      setResizingIndex(null);
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  }, [orientation, minSizes, maxSizes]);

  useEffect(() => {
    onResize?.(sizes);
  }, [sizes, onResize]);

  const panels = React.Children.toArray(children);

  return (
    <div
      ref={containerRef}
      className={cn(
        "flex",
        orientation === 'horizontal' ? "flex-row h-full" : "flex-col w-full",
        className
      )}
    >
      {panels.map((panel, index) => (
        <React.Fragment key={index}>
          <div
            className={cn(
              "relative",
              orientation === 'horizontal' ? "h-full" : "w-full"
            )}
            style={{
              [orientation === 'horizontal' ? 'width' : 'height']: `${sizes[index]}%`
            }}
          >
            {panel}
          </div>
          
          {index < panels.length - 1 && (
            <ResizeHandle
              orientation={orientation}
              isResizing={isResizing && resizingIndex === index}
              onMouseDown={(e) => startResize(e, index)}
            />
          )}
        </React.Fragment>
      ))}
    </div>
  );
};

// Preset panel layouts
export const TwoColumnLayout: React.FC<{
  left: React.ReactNode;
  right: React.ReactNode;
  defaultSizes?: [number, number];
  className?: string;
}> = ({ left, right, defaultSizes = [30, 70], className }) => (
  <ResizablePanels
    orientation="horizontal"
    defaultSizes={defaultSizes}
    minSizes={[20, 30]}
    maxSizes={[50, 80]}
    className={className}
  >
    {left}
    {right}
  </ResizablePanels>
);

export const ThreeColumnLayout: React.FC<{
  left: React.ReactNode;
  center: React.ReactNode;
  right: React.ReactNode;
  defaultSizes?: [number, number, number];
  className?: string;
}> = ({ left, center, right, defaultSizes = [25, 50, 25], className }) => (
  <ResizablePanels
    orientation="horizontal"
    defaultSizes={defaultSizes}
    minSizes={[15, 30, 15]}
    maxSizes={[40, 70, 40]}
    className={className}
  >
    {left}
    {center}
    {right}
  </ResizablePanels>
);

export const TwoRowLayout: React.FC<{
  top: React.ReactNode;
  bottom: React.ReactNode;
  defaultSizes?: [number, number];
  className?: string;
}> = ({ top, bottom, defaultSizes = [60, 40], className }) => (
  <ResizablePanels
    orientation="vertical"
    defaultSizes={defaultSizes}
    minSizes={[30, 20]}
    maxSizes={[80, 70]}
    className={className}
  >
    {top}
    {bottom}
  </ResizablePanels>
);

export default ResizablePanels;