import React from 'react';
import {ink} from '../../../kit/style';
import type {DrawContext, Prop} from '../../../kit/types';

// A single open notebook with cream pages and a pen resting across it.
const Notebook: React.FC<DrawContext> = () => (
	<g filter="url(#softEdge)">
		<path d="M-110,0 L-96,-30 L0,-22 L96,-30 L110,0 L0,6 Z" fill="#5d7f91" {...ink(2.5)} />
		<path d="M-100,-4 L-88,-30 L0,-24 L0,2 Z" fill="#fbf7ee" {...ink(2)} />
		<path d="M100,-4 L88,-30 L0,-24 L0,2 Z" fill="#f6f1e4" {...ink(2)} />
		<path d="M-80,-20 L-12,-16 M-82,-12 L-12,-8 M12,-16 L80,-20 M12,-8 L82,-12" stroke="#b9c3cc" strokeWidth={2} />
		<path d="M20,-30 L96,-44" stroke="#2c2f36" strokeWidth={7} strokeLinecap="round" />
		<path d="M20,-30 L30,-32" stroke="#d9b25c" strokeWidth={7} strokeLinecap="round" />
	</g>
);

export const prop: Prop = {id: 'open-notebook', width: 220, Component: Notebook};
