import React from 'react';

// "Coin" from Microsoft Fluent Emoji (Flat style), MIT License: see ./LICENSE.
// Drawn from its original 32x32 box with the origin at the bottom centre; `size` is the height in px,
// `recolor` swaps any original colour, and a soft ink outline matches the series' look.
export const Coin: React.FC<{size?: number; recolor?: Record<string, string>}> = ({size = 100, recolor}) => (
	<g transform={`scale(${size / 32}) translate(-16 -31)`} stroke="#3b2a20" strokeWidth={0.45} strokeLinejoin="round" paintOrder="stroke">
		<path d="M16 30C23.732 30 30 23.732 30 16C30 8.26801 23.732 2 16 2C8.26801 2 2 8.26801 2 16C2 23.732 8.26801 30 16 30Z" fill={recolor?.['#F9C23C'] ?? '#F9C23C'} />
		<path d="M27 16C27 22.0751 22.0751 27 16 27C9.92487 27 5 22.0751 5 16C5 9.92487 9.92487 5 16 5C22.0751 5 27 9.92487 27 16ZM22.32 19.89C22.25 19.67 22.04 19.52 21.81 19.52H21.84V11.76C22.27 11.48 22.35 10.79 21.83 10.48L16.44 7.22004C16.2 7.07004 15.9 7.07004 15.66 7.22004L10.26 10.48C9.74 10.79 9.82 11.48 10.24 11.76V19.53H10.13C9.89 19.53 9.68 19.69 9.62 19.92L9.27 21.17C9.17 21.51 9.43 21.85 9.78 21.85H22.23C22.58 21.84 22.84 21.49 22.73 21.14L22.32 19.89ZM11.9 11.88V19.52H13.56V11.88H11.9ZM15.21 11.88V19.52H16.9V11.88H15.21ZM18.56 11.88V19.52H20.18V11.88H18.56Z" fill={recolor?.['#D3883E'] ?? '#D3883E'} />
	</g>
);
