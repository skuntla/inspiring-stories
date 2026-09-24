import React from 'react';
import {ink} from '../../../kit/style';
import type {DrawContext, Prop} from '../../../kit/types';

// A brass tumbler brimming with water that catches the light.
const Cup: React.FC<DrawContext> = ({t}) => (
	<g>
		<path d="M-20,0 L-24,-56 L24,-56 L20,0 Z" fill="#d9a441" {...ink(2.5)} />
		<ellipse cx={0} cy={-56} rx={24} ry={5} fill="#8fc3e0" {...ink(1.5)} />
		<path d="M-12,-46 L-10,-8" stroke="#f4e2a0" strokeWidth={4} strokeLinecap="round" opacity={0.7 + 0.2 * Math.sin(t * 3)} />
	</g>
);
export const prop: Prop = {id: 'water-cup', width: 60, Component: Cup};
