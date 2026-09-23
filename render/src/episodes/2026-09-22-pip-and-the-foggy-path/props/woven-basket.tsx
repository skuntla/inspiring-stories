import React from 'react';
import {ink} from '../../../kit/style';
import type {DrawContext, Prop} from '../../../kit/types';

// A small oval basket woven from pale willow branches, with a curved handle and a cream cloth lining.
const Basket: React.FC<DrawContext> = () => (
	<g filter="url(#softEdge)">
		<path d="M-50,-50 C-50,-110 50,-110 50,-50" fill="none" stroke="#3b2a20" strokeWidth={11} strokeLinecap="round" />
		<path d="M-50,-50 C-50,-110 50,-110 50,-50" fill="none" stroke="#d2b07a" strokeWidth={5} />
		<path d="M-58,-52 C-60,-20 -40,0 0,0 C40,0 60,-20 58,-52 Z" fill="#d2b07a" {...ink(3)} />
		<path d="M-54,-52 C-30,-66 30,-66 54,-52 C30,-44 -30,-44 -54,-52 Z" fill="#f3ead6" {...ink(2.5)} />
		{[-40, -20, 0, 20, 40].map((x) => <path key={x} d={`M${x},-46 L${x * 0.8},-4`} stroke="#b08a52" strokeWidth={2} />)}
		{[-36, -22].map((y) => <path key={y} d={`M-54,${y} C-20,${y + 6} 20,${y + 6} 54,${y}`} fill="none" stroke="#b08a52" strokeWidth={2} />)}
	</g>
);

export const prop: Prop = {id: 'woven-basket', width: 120, Component: Basket};
