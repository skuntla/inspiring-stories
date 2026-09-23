import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Defs, palette} from '../kit/style';
import type {Rig} from '../kit/types';
import {rig as ben} from '../series/willow-meadow/characters/ben';
import {rig as pip} from '../series/willow-meadow/characters/pip';
import {rig as wren} from '../series/willow-meadow/characters/wren';
import {rig as arjun} from '../series/quiet-lessons/characters/arjun';
import {rig as gardener} from '../series/quiet-lessons/characters/gardener';

// Dev only: every supported stance of each Willow Meadow rig, cycling through moods, mid-speech on odd cells.
const ROWS: {rig: Rig; scale: number}[] = [{rig: pip, scale: 0.4}, {rig: ben, scale: 0.3}, {rig: wren, scale: 0.6},
	{rig: arjun, scale: 0.38}, {rig: gardener, scale: 0.38}];
const SHAPES = ['rest', 'open', 'ee', 'round'] as const;

export const RigSheet: React.FC = () => {
	const pal = palette('morning');
	return (
		<AbsoluteFill style={{backgroundColor: '#efe7d4'}}>
			<svg viewBox="0 0 1920 1080" width="100%" height="100%">
				<Defs palette={pal} />
				{ROWS.map(({rig, scale}, r) =>
					rig.stances.map((stance, i) => {
						const mood = rig.moods[(i * 3 + r) % rig.moods.length];
						const x = 150 + i * 255;
						const y = 190 + r * 212;
						return (
							<g key={`${r}-${i}`}>
								<g transform={`translate(${x} ${y}) scale(${scale})`}>
									<rig.Component t={1.2} palette={pal} timeOfDay="morning" stance={stance} mood={mood}
										mouth={SHAPES[i % SHAPES.length]} eye={1} speaking={i % 2 === 1} facing="right" />
								</g>
								<text x={x} y={y + 26} fontSize={18} fontFamily="system-ui" textAnchor="middle" fill="#3b2a20">
									{rig.id}: {stance} / {mood}
								</text>
							</g>
						);
					}),
				)}
			</svg>
		</AbsoluteFill>
	);
};
