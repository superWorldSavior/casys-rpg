import React from 'react';

const Logo: React.FC<{ size?: number; color?: string }> = ({ 
  size = 512, 
  color = '#4F46E5' 
}) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 512 512"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <rect width="512" height="512" rx="128" fill={color} />
    <path
      d="M256 128C279.196 128 298 146.804 298 170V342C298 365.196 279.196 384 256 384C232.804 384 214 365.196 214 342V170C214 146.804 232.804 128 256 128Z"
      fill="white"
    />
    <path
      d="M354 226C365.046 226 374 234.954 374 246V266C374 277.046 365.046 286 354 286C342.954 286 334 277.046 334 266V246C334 234.954 342.954 226 354 226Z"
      fill="white"
    />
    <path
      d="M158 226C169.046 226 178 234.954 178 246V266C178 277.046 169.046 286 158 286C146.954 286 138 277.046 138 266V246C138 234.954 146.954 226 158 226Z"
      fill="white"
    />
  </svg>
);

export default Logo;
