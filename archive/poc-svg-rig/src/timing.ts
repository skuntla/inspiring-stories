import timeline from './timeline.json';

export type Shape = 'rest' | 'closed' | 'fv' | 'consonant' | 'ee' | 'mid' | 'open' | 'round';
export type Word = {text: string; start: number; end: number};
export type Line = {
	speaker: string;
	text: string;
	start: number;
	end: number;
	words: Word[];
	visemes: {t: number; shape: string}[];
};

export const FPS = timeline.fps;
export const DURATION = timeline.durationInFrames;
export const LINES = timeline.lines as Line[];

export const lineAt = (seconds: number): Line | undefined =>
	LINES.find((l) => seconds >= l.start && seconds <= l.end);

/** The mouth shape a speaker shows at a time: the latest viseme key at or before it. */
export const mouthAt = (speaker: string, seconds: number): Shape => {
	const line = LINES.find((l) => l.speaker === speaker && seconds >= l.start && seconds <= l.end);
	if (!line) return 'rest';
	let shape: Shape = 'rest';
	for (const v of line.visemes) {
		if (v.t > seconds) break;
		shape = v.shape as Shape;
	}
	return shape;
};

export const isSpeaking = (speaker: string, seconds: number) => mouthAt(speaker, seconds) !== 'rest';

/** Blink openness 0..1 (0 = fully closed) on a fixed, seeded schedule. */
export const eyeOpenness = (frame: number): number => {
	const blinks = [38, 131, 212, 268, 355, 402];
	for (const b of blinks) {
		const d = frame - b;
		if (d >= 0 && d < 6) return [0.55, 0.1, 0, 0.15, 0.6, 1][d];
	}
	return 1;
};
