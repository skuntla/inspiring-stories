import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Defs, palette} from '../kit/style';
import {rig as arjun} from '../series/quiet-lessons/characters/arjun';

// Dev only: how Arjun's posture and gesture change with mood, standing and seated.
const MOODS = ['neutral', 'happy', 'worried', 'thoughtful', 'sad', 'surprised', 'calm'];

export const ActingSheet: React.FC = () => {
	const pal = palette('morning');
	return (
		<AbsoluteFill style={{backgroundColor: '#efe7d4'}}>
			<svg viewBox="0 0 1920 1080" width="100%" height="100%">
				<Defs palette={pal} />
				{['stand', 'sit'].map((stance, r) =>
					MOODS.map((mood, i) => {
						const x = 150 + i * 265;
						const y = 470 + r * 500;
						return (
							<g key={`${stance}-${mood}`}>
								{stance === 'sit' && <rect x={x - 70} y={y - 122} width={170} height={20} rx={6} fill="#9a6a42" />}
								<g transform={`translate(${x} ${y}) scale(0.85)`}>
									<arjun.Component t={1.3} palette={pal} timeOfDay="morning" stance={stance} mood={mood} mouth="rest" eye={1}
										speaking={false} facing="right" />
								</g>
								<text x={x} y={y + 40} fontSize={24} fontFamily="system-ui" textAnchor="middle" fill="#3b2a20">{stance} / {mood}</text>
							</g>
						);
					}),
				)}
			</svg>
		</AbsoluteFill>
	);
};
