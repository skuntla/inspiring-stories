import React from 'react';
import {Grass, Hills, Mint} from '../../../kit/scenery';
import {ink} from '../../../kit/style';
import type {DrawContext, Location} from '../../../kit/types';

// A round wooden doorway beneath the roots of a great oak tree, surrounded by moss and wild mint.
const DOOR_X = 1250;

const Background: React.FC<DrawContext> = ({t, palette: p}) => {
	const glow = 0.85 + 0.1 * Math.sin(t * 3) + (1 - p.light) * 0.5;
	return (
		<g>
			<g filter="url(#farBlur)"><Hills y={600} amp={60} color="#a4b3a0" seed={21} outline={0.15} /></g>
			<g filter="url(#watercolor)">
				{/* the great oak: a wide trunk whose roots arch over the door */}
				<ellipse cx={DOOR_X} cy={150} rx={620} ry={260} fill="#7f9a5c" {...ink(3, 0.6)} />
				<ellipse cx={DOOR_X - 420} cy={260} rx={300} ry={170} fill="#88a262" {...ink(3, 0.6)} />
				<ellipse cx={DOOR_X + 440} cy={250} rx={320} ry={180} fill="#88a262" {...ink(3, 0.6)} />
				<path d={`M${DOOR_X - 330},860 C${DOOR_X - 260},700 ${DOOR_X - 200},480 ${DOOR_X - 150},300 L${DOOR_X + 150},300 C${DOOR_X + 210},480 ${DOOR_X + 270},700 ${DOOR_X + 360},860 Z`}
					fill="#7a5a3c" {...ink(3.5)} />
				<Hills y={830} amp={20} color="#8ba06a" seed={23} waves={3} outline={0.45} />
			</g>
			{/* roots, doorway and warm light */}
			<ellipse cx={DOOR_X} cy={640} rx={260 * glow} ry={220 * glow} fill="url(#warmGlow)" />
			<path d={`M${DOOR_X - 110},850 L${DOOR_X - 110},650 C${DOOR_X - 110},560 ${DOOR_X + 110},560 ${DOOR_X + 110},650 L${DOOR_X + 110},850 Z`}
				fill="#ffcf7a" {...ink(3.5)} />
			<path d={`M${DOOR_X - 90},850 L${DOOR_X - 90},660 C${DOOR_X - 90},590 ${DOOR_X - 5},590 ${DOOR_X - 5},590 L${DOOR_X - 5},850 Z`}
				fill="#8a5e36" {...ink(3)} />
			<circle cx={DOOR_X - 24} cy={740} r={7} fill="#c9a13b" {...ink(2)} />
			<path d={`M${DOOR_X - 200},860 C${DOOR_X - 170},760 ${DOOR_X - 120},640 ${DOOR_X - 60},560 M${DOOR_X + 220},860 C${DOOR_X + 180},760 ${DOOR_X + 130},640 ${DOOR_X + 70},560`}
				fill="none" stroke="#6a4c30" strokeWidth={34} strokeLinecap="round" />
			<path d={`M${DOOR_X - 150},860 C${DOOR_X - 60},820 ${DOOR_X + 80},820 ${DOOR_X + 170},860`} fill="#6f8f45" {...ink(2.5)} />
			<Mint x={DOOR_X - 250} y={870} seed={3} />
			<Mint x={DOOR_X + 260} y={872} scale={0.9} seed={5} />
			<Grass y={880} count={50} height={50} color="#7d9360" seed={27} />
		</g>
	);
};

const Foreground: React.FC<DrawContext> = ({t}) => (
	<g filter="url(#softEdge)">
		<Grass y={1150} count={36} height={160} color="#6c8450" seed={29} sway={Math.sin(t * 1.4) * 6} />
	</g>
);

export const location: Location = {
	id: 'ben-burrow-exterior',
	groundY: 872,
	backgroundGroundY: 820,
	propSlots: [[560, 882], [700, 886], [1500, 874]],
	Background,
	Foreground,
};
