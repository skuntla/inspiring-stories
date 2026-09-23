import React from 'react';
import {AbsoluteFill} from 'remotion';
import {thumbnail} from '../generated/registry';
import {Defs, Sky, palette} from '../kit/style';
import type {DrawContext, Location, Rig, TimeOfDay} from '../kit/types';

// YouTube thumbnails, drawn from the same components as the episode so the faces match the video.
// An episode describes its thumbnail in render/src/episodes/<episode>/thumbnail.tsx (a ThumbnailSpec);
// `story thumbnail` renders one image per headline variant.

export type ThumbCharacter = {
	rig: Rig;
	stance: string;
	mood: string;
	facing: 'left' | 'right';
	x: number; // scene x of the feet
	ground: number; // scene y of the feet (below the frame crops the body)
	scale: number;
};

export type ThumbnailSpec = {
	background: Location;
	/** The part of the scene behind the characters: [center x, center y, zoom]; default the whole scene. */
	view?: [number, number, number];
	timeOfDay: TimeOfDay;
	characters: ThumbCharacter[];
	/** Drawn in scene coordinates between the characters: the story's central image. */
	Center?: React.FC<DrawContext>;
	/** One per variant, on one line each so `story thumbnail` can count them. `*word*` is highlighted,
	 * `\n` breaks the line; keep it to about five words. */
	headlines: string[];
};

const HEAVY = '"Arial Black", "Helvetica Neue", Arial, sans-serif';
const YELLOW = '#ffd23f';

const Headline: React.FC<{text: string}> = ({text}) => {
	const lines = text.split('\n');
	const size = Math.max(...lines.map((l) => l.replace(/\*/g, '').length)) > 18 ? 118 : 138;
	return (
		<g fontFamily={HEAVY} fontWeight={900} fontSize={size} textAnchor="middle" letterSpacing={1}>
			{lines.map((line, i) => (
				<text key={i} x={960} y={150 + i * size * 1.02} stroke="#1c140e" strokeWidth={16} strokeLinejoin="round" paintOrder="stroke" fill="#ffffff">
					{line.split(/(\*[^*]+\*)/).filter(Boolean).map((part, j) =>
						part.startsWith('*') ? <tspan key={j} fill={YELLOW}>{part.slice(1, -1)}</tspan> : <tspan key={j}>{part}</tspan>,
					)}
				</text>
			))}
		</g>
	);
};

export const Thumbnail: React.FC<{variant: number}> = ({variant}) => {
	if (!thumbnail) return <AbsoluteFill style={{backgroundColor: '#333'}} />;
	const {background: Bg, view = [960, 560, 1.12], timeOfDay, characters, Center, headlines} = thumbnail;
	const pal = palette(timeOfDay);
	const ctx: DrawContext = {t: 2, palette: pal, timeOfDay, words: []};
	return (
		<AbsoluteFill style={{backgroundColor: '#000'}}>
			<svg viewBox="0 0 1920 1080" width="100%" height="100%">
				<Defs palette={pal} />
				{/* the place, soft and slightly zoomed, so the faces and words carry the image */}
				<g filter="url(#farBlur)" transform={`translate(960 540) scale(${view[2]}) translate(${-view[0]} ${-view[1]})`}>
					{!Bg.interior && <Sky palette={pal} />}
					<Bg.Background {...ctx} />
				</g>
				<rect width={1920} height={1080} fill={pal.tint} opacity={pal.tintOpacity} style={{mixBlendMode: 'multiply'}} />
				<defs>
					<linearGradient id="thumbTop" x1="0" y1="0" x2="0" y2="1">
						<stop offset="0" stopColor="#000" stopOpacity={0.55} />
						<stop offset="1" stopColor="#000" stopOpacity={0} />
					</linearGradient>
				</defs>
				<rect width={1920} height={420} fill="url(#thumbTop)" />
				{Center && <Center {...ctx} />}
				{characters.map((c, i) => (
					<g key={i} transform={`translate(${c.x} ${c.ground}) scale(${(c.facing === 'left' ? -1 : 1) * c.scale} ${c.scale})`}>
						<c.rig.Component {...ctx} stance={c.stance} mood={c.mood} mouth="rest" eye={1} speaking={false} facing={c.facing} />
					</g>
				))}
				<Headline text={headlines[Math.min(variant, headlines.length - 1)]} />
			</svg>
		</AbsoluteFill>
	);
};
