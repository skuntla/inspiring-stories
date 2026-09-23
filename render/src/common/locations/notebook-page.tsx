import React from 'react';
import {ink} from '../../kit/style';
import {sentences, wrap} from '../../kit/spoken';
import type {DrawContext, Location, SpokenWord} from '../../kit/types';

// Close on an open notebook under lamplight. What a character reads out in this shot writes itself
// on the right-hand page, each line in step with the voice (the narrator's lead-in is not written).
export const about = "Close-up of an open notebook; the character's spoken line writes itself on the page as it is read out.";

const X0 = 1000;
const WIDTH = 660;
const FONT = '"Bradley Hand", "Segoe Print", "Comic Sans MS", cursive';
const CHARS = 24; // per written row at this size

type Row = {text: string; from: number; to: number};

/** The written rows: the characters' sentences (or every sentence, if only the narrator speaks), wrapped
 * to the page, each row taking its share of its sentence's spoken time. */
const rowsFor = (words: SpokenWord[] | undefined): Row[] => {
	const all = sentences(words);
	const said = all.some((s) => s.speaker) ? all.filter((s) => s.speaker) : all;
	return said.flatMap((s) => {
		const parts = wrap(s.text, CHARS);
		const total = parts.reduce((n, p) => n + p.length, 0);
		let at = s.from;
		return parts.map((text) => {
			const span = ((s.to - s.from) * text.length) / total;
			const row = {text, from: at, to: at + span};
			at += span;
			return row;
		});
	});
};

const progress = (t: number, from: number, to: number) => Math.max(0, Math.min(1, (t - from) / (to - from)));

const Background: React.FC<DrawContext> = ({t, words}) => {
	const LINES = React.useMemo(() => rowsFor(words), [words]);
	const gap = LINES.length > 4 ? Math.min(130, 500 / (LINES.length - 1)) : 130; // keep every row on the page
	const active = LINES.findIndex((l) => t >= l.from && t < l.to + 0.2);
	const pen = active >= 0 ? [X0 + WIDTH * progress(t, LINES[active].from, LINES[active].to) * 0.9, 430 + active * gap] : [1560, 760];
	return (
		<g>
			<rect x={-200} y={-200} width={2320} height={1480} fill="#6b4630" />
			<circle cx={1400} cy={200} r={900} fill="url(#warmGlow)" opacity={0.8} />
			<g filter="url(#softEdge)">
				<path d="M200,140 L940,110 L960,1000 L230,1010 Z" fill="#fbf7ee" {...ink(4)} />
				<path d="M960,110 L1700,140 L1670,1010 L960,1000 Z" fill="#f6f1e4" {...ink(4)} />
				<path d="M960,110 L960,1000" stroke="#c9bfa8" strokeWidth={6} />
				{Array.from({length: 11}).map((_, i) => (
					<g key={i}>
						<path d={`M270,${250 + i * 65} L900,${250 + i * 65}`} stroke="#c7d3de" strokeWidth={2} />
						<path d={`M1010,${250 + i * 65} L1630,${250 + i * 65}`} stroke="#c7d3de" strokeWidth={2} />
					</g>
				))}
				<text x={300} y={225} fontSize={44} fontFamily={FONT} fill="#8a7a66">Page 1</text>
			</g>
			<defs>
				{LINES.map((l, i) => (
					<clipPath key={i} id={`reveal-${i}`}>
						<rect x={X0 - 10} y={330 + i * gap} width={(WIDTH + 20) * progress(t, l.from, l.to)} height={130} />
					</clipPath>
				))}
			</defs>
			{LINES.map((l, i) => (
				<text key={i} x={X0} y={430 + i * gap} fontSize={60} fontFamily={FONT} fill="#23304a" clipPath={`url(#reveal-${i})`}>
					{l.text}
				</text>
			))}
			{/* the pen follows the writing */}
			<g transform={`translate(${pen[0]} ${pen[1]}) rotate(-35)`}>
				<rect x={-10} y={-190} width={20} height={180} rx={8} fill="#2c2f36" {...ink(3)} />
				<rect x={-10} y={-190} width={20} height={40} rx={8} fill="#d9b25c" {...ink(2.5)} />
				<path d="M-10,-10 L0,12 L10,-10 Z" fill="#c9a13b" {...ink(2.5)} />
			</g>
		</g>
	);
};

export const location: Location = {
	id: 'notebook-page',
	interior: true,
	groundY: 880,
	propSlots: [],
	showsText: true,
	Background,
};
