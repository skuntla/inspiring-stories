import React from 'react';
import {INK} from './style';
import type {Shape} from './types';

/** How a mood shapes the face: lid openness, eye scale, brow tilt/lift, and the resting mouth. */
export type MoodFace = {lid: number; eyeScale: number; browTilt: number; browLift: number; rest: string; tear?: boolean};

export const MOODS: Record<string, MoodFace> = {
	neutral: {lid: 1, eyeScale: 1, browTilt: 0, browLift: 0, rest: 'M-12,-1 Q0,5 12,-1'},
	happy: {lid: 0.85, eyeScale: 1, browTilt: -4, browLift: -3, rest: 'M-14,-3 Q0,10 14,-3'},
	sad: {lid: 0.75, eyeScale: 0.95, browTilt: 14, browLift: 2, rest: 'M-11,4 Q0,-4 11,4', tear: true},
	surprised: {lid: 1, eyeScale: 1.18, browTilt: -6, browLift: -9, rest: 'M-5,0 A5,6 0 1,0 5,0 A5,6 0 1,0 -5,0'},
	worried: {lid: 0.9, eyeScale: 1.05, browTilt: 16, browLift: -4, rest: 'M-12,2 Q-6,-2 0,2 Q6,5 12,1'},
	scared: {lid: 1, eyeScale: 1.2, browTilt: 18, browLift: -8, rest: 'M-9,-2 Q0,8 9,-2 Q0,3 -9,-2 Z'},
	angry: {lid: 0.8, eyeScale: 1, browTilt: -18, browLift: 3, rest: 'M-11,2 L11,0'},
	thoughtful: {lid: 0.8, eyeScale: 1, browTilt: 8, browLift: -2, rest: 'M-10,1 Q2,3 12,-3'},
	proud: {lid: 0.8, eyeScale: 1, browTilt: -6, browLift: -2, rest: 'M-13,-2 Q0,8 13,-2'},
	tired: {lid: 0.55, eyeScale: 0.95, browTilt: 8, browLift: 3, rest: 'M-10,1 Q0,3 10,1'},
};

export const moodFace = (mood: string): MoodFace => MOODS[mood] ?? MOODS.neutral;

const INSIDE = '#5a2630';
const TONGUE = '#c9606f';
const TEETH = '#fbf6ec';

/** The mouth, drawn around (0,0): a viseme while speaking, the mood's resting shape otherwise. */
export const Mouth: React.FC<{shape: Shape; mood: string}> = ({shape, mood}) => {
	const edge = {stroke: INK, strokeWidth: 2.4, strokeLinejoin: 'round' as const};
	switch (shape) {
		case 'closed':
			return <path d="M-13,0 Q0,2 13,0" fill="none" stroke={INK} strokeWidth={4} strokeLinecap="round" />;
		case 'fv':
			return (
				<g>
					<path d="M-12,-2 Q0,9 12,-2 Z" fill={INSIDE} {...edge} />
					<rect x={-7} y={-3} width={14} height={4} rx={1.5} fill={TEETH} />
				</g>
			);
		case 'consonant':
			return (
				<g>
					<path d="M-13,-2 Q0,11 13,-2 Q0,2 -13,-2 Z" fill={INSIDE} {...edge} />
					<path d="M-8,-1 L8,-1" stroke={TEETH} strokeWidth={3} strokeLinecap="round" />
				</g>
			);
		case 'ee':
			return (
				<g>
					<path d="M-16,-3 Q0,11 16,-3 Q0,0 -16,-3 Z" fill={INSIDE} {...edge} />
					<path d="M-10,-1.5 L10,-1.5" stroke={TEETH} strokeWidth={2.5} strokeLinecap="round" />
				</g>
			);
		case 'mid':
			return (
				<g>
					<path d="M-13,-3 Q0,16 13,-3 Q0,-1 -13,-3 Z" fill={INSIDE} {...edge} />
					<ellipse cx={0} cy={6} rx={6} ry={3} fill={TONGUE} />
				</g>
			);
		case 'open':
			return (
				<g>
					<path d="M-12,-4 Q0,24 12,-4 Q0,-2 -12,-4 Z" fill={INSIDE} {...edge} />
					<ellipse cx={0} cy={11} rx={7} ry={4} fill={TONGUE} />
				</g>
			);
		case 'round':
			return <ellipse cx={0} cy={3} rx={6.5} ry={8} fill={INSIDE} {...edge} />;
		default: {
			const face = moodFace(mood);
			const filled = face.rest.endsWith('Z') || mood === 'surprised';
			return <path d={face.rest} fill={filled ? INSIDE : 'none'} stroke={INK} strokeWidth={3.2} strokeLinecap="round" />;
		}
	}
};

/** How far a beak opens (0..1) for each viseme: for bird-like characters. */
export const BEAK_OPEN: Record<Shape, number> = {rest: 0, closed: 0, fv: 0.25, consonant: 0.3, ee: 0.35, mid: 0.6, open: 1, round: 0.5};
