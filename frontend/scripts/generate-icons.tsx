import React from 'react';
import * as ReactDOMServer from 'react-dom/server';
import sharp from 'sharp';
import { writeFileSync } from 'fs';
import Logo from '../src/components/Logo';

const sizes = [192, 512];

async function generateIcons() {
  try {
    for (const size of sizes) {
      const svg = ReactDOMServer.renderToString(
        <Logo size={size} />
      );
      
      // Write SVG to a temporary file
      const tempSvgPath = `frontend/public/temp-${size}.svg`;
      writeFileSync(tempSvgPath, svg);
      
      // Convert SVG to PNG using sharp
      await sharp(tempSvgPath)
        .resize(size, size)
        .png()
        .toFile(`frontend/public/icon-${size}x${size}.png`);
        
      // Clean up temporary SVG
      await sharp(tempSvgPath).png().toFile(`frontend/public/icon-${size}x${size}.png`);
      // Use fs module directly
      const fs = require('fs');
      fs.unlinkSync(tempSvgPath);
    }
    console.log('Icons generated successfully!');
  } catch (error) {
    console.error('Error generating icons:', error);
  }
}

generateIcons();
