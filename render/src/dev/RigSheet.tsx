import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Defs, palette} from '../kit/style';
import type {Rig} from '../kit/types';
import {rig as ben} from '../series/willow-meadow/characters/ben';
import {rig as pip} from '../series/willow-meadow/characters/pip';
import {rig as wren} from '../series/willow-meadow/characters/wren';

// Dev only: every supported stance of each Willow Meadow rig, cycling through moods, mid-speech on odd cells.
const ROWS: {rig: Rig; scale: number}[] = [{rig: pip, scale: 0.62}, {rig: ben, scale: 0.46}, {rig: wren, scale: 0.9}];
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
						const y = 320 + r * 330;
						return (
							<g key={`${r}-${i}`}>
								<g transform={`translate(${x} ${y}) scale(${scale})`}>
									<rig.Component t={1.2} palette={pal} timeOfDay="morning" stance={stance} mood={mood}
										mouth={SHAPES[i % SHAPES.length]} eye={1} speaking={i % 2 === 1} facing="right" />
								</g>
								<text x={x} y={y + 40} fontSize={22} fontFamily="system-ui" textAnchor="middle" fill="#3b2a20">
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
