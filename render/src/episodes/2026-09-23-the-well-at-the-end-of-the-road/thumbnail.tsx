import React from 'react';
import {rig as velu} from '../../series/quiet-lessons/characters/velu';
import {rig as villager} from '../../series/quiet-lessons/characters/villager';
import type {ThumbnailSpec} from '../../thumbnail/Thumbnail';
import {location as plot} from './locations/velu-plot';
import {StoneWell} from './parts/village';

// Velu digging (left) and the villager laughing at him (right), with the story's payoff between them:
// a well overflowing with clear water.
const Burst: React.FC<{t: number}> = ({t}) => (
	<g transform="translate(960 900)">
		<StoneWell x={0} y={0} t={t} scale={1.1} />
		{Array.from({length: 16}).map((_, i) => {
			const a = -Math.PI * (0.12 + (i / 15) * 0.76);
			return <path key={i} d={`M0,-190 q${Math.cos(a) * 120},${Math.sin(a) * 160 - 60} ${Math.cos(a) * 240},${Math.sin(a) * 120 + 60}`} fill="none"
				stroke="#8fc3e0" strokeWidth={14} strokeLinecap="round" opacity={0.85} />;
		})}
		{Array.from({length: 14}).map((_, i) => (
			<circle key={`d${i}`} cx={Math.cos(i * 0.9) * (180 + (i % 3) * 60)} cy={-300 - Math.abs(Math.sin(i * 1.7)) * 160} r={10 + (i % 3) * 3} fill="#cfe8f5" />
		))}
	</g>
);

export const thumbnail: ThumbnailSpec = {
	background: plot,
	view: [960, 600, 1.15],
	timeOfDay: 'morning',
	characters: [
		{rig: velu, stance: 'dig', mood: 'calm', facing: 'right', x: 250, ground: 1250, scale: 1.55},
		{rig: villager, stance: 'reach', mood: 'happy', facing: 'left', x: 1640, ground: 1290, scale: 1.6},
	],
	Center: ({t}) => <Burst t={t} />,
	headlines: ['THEY *LAUGHED* AT HIM\nFOR *TEN YEARS*', 'DISCIPLINE *BEATS*\nLOCATION', 'DIG YOUR *WELL*'],
};
