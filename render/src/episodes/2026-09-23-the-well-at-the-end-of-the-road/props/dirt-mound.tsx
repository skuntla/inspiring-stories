import React from 'react';
import {ink} from '../../../kit/style';
import type {DrawContext, Prop} from '../../../kit/types';

// The heap of earth and broken rock Velu has dug out of the pit.
const Mound: React.FC<DrawContext> = () => (
	<g>
		<path d="M-170,0 C-140,-70 -60,-130 0,-130 C70,-130 140,-70 170,0 Z" fill="#a8845c" {...ink(3)} />
		{[[-80, -40, 22], [20, -80, 18], [90, -30, 26], [-20, -20, 16]].map(([x, y, r], i) => (
			<ellipse key={i} cx={x} cy={y} rx={r} ry={r * 0.7} fill="#8a7058" {...ink(2)} />
		))}
	</g>
);
export const prop: Prop = {id: 'dirt-mound', width: 340, Component: Mound};
