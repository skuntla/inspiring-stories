import React from 'react';
import {ink} from '../../../kit/style';
import type {DrawContext, Prop} from '../../../kit/types';

// A small round brass compass; its red-tipped needle wobbles and then settles on north.
export const needleAngle = (t: number) => 55 * Math.exp(-t * 0.7) * Math.cos(t * 3.2);

const Compass: React.FC<DrawContext> = ({t}) => (
	<g filter="url(#softEdge)" transform="translate(0 -36)">
		<circle cx={0} cy={0} r={36} fill="#c9a13b" {...ink(3)} />
		<circle cx={0} cy={0} r={28} fill="#f6efdc" {...ink(2)} />
		<text x={0} y={-16} textAnchor="middle" fontSize={11} fontFamily="Georgia, serif" fill="#3b2a20">N</text>
		<g transform={`rotate(${needleAngle(t)})`}>
			<path d="M0,-22 L5,0 L-5,0 Z" fill="#c8323a" />
			<path d="M0,22 L5,0 L-5,0 Z" fill="#3b3a3a" />
		</g>
		<circle cx={0} cy={0} r={3} fill="#8a6a2e" />
		<circle cx={0} cy={-40} r={6} fill="none" stroke="#c9a13b" strokeWidth={4} />
	</g>
);

export const prop: Prop = {id: 'brass-compass', width: 80, Component: Compass};
