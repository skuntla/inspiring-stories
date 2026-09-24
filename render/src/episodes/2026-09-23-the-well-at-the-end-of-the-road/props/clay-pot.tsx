import React from 'react';
import {ink} from '../../../kit/style';
import type {DrawContext, Prop} from '../../../kit/types';

// A round terracotta water pot (matka) with a short neck and a white painted band.
const Pot: React.FC<DrawContext> = () => (
	<g>
		<path d="M-40,-6 C-54,-56 -24,-84 0,-84 C24,-84 54,-56 40,-6 Q0,6 -40,-6 Z" fill="#b5602f" {...ink(3)} />
		<path d="M-15,-84 L-17,-100 L17,-100 L15,-84" fill="#a3542a" {...ink(2.5)} />
		<path d="M-44,-44 Q0,-32 44,-44" fill="none" stroke="#f4efe2" strokeWidth={4} />
		<path d="M-30,-60 q4,-10 10,-12" fill="none" stroke="#e08a5a" strokeWidth={4} strokeLinecap="round" />
	</g>
);
export const prop: Prop = {id: 'clay-pot', width: 100, Component: Pot};
