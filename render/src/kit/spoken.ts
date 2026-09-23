import type {SpokenWord} from './types';

export type Sentence = {text: string; from: number; to: number; speaker: string | null};

/** The shot's words grouped into sentences (split at . ! ? and wherever the speaker changes). */
export const sentences = (words: SpokenWord[] = []): Sentence[] => {
	const out: Sentence[] = [];
	let open: Sentence | null = null;
	for (const w of words) {
		if (!open || open.speaker !== w.speaker) {
			open = {text: w.text, from: w.from, to: w.to, speaker: w.speaker};
			out.push(open);
		} else {
			open.text += ` ${w.text}`;
			open.to = w.to;
		}
		if (/[.!?]["”']?$/.test(w.text)) open = null;
	}
	return out;
};

/** When the shot's last word starts (seconds), or `fallback` when nothing is spoken. */
export const lastWordAt = (words: SpokenWord[] = [], fallback = 3) => (words.length ? words[words.length - 1].from : fallback);

/** Greedy word wrap for SVG text, which has no line breaking of its own. */
export const wrap = (text: string, maxChars: number): string[] => {
	const lines: string[] = [];
	for (const word of text.split(/\s+/)) {
		const last = lines[lines.length - 1];
		if (last !== undefined && `${last} ${word}`.length <= maxChars) lines[lines.length - 1] = `${last} ${word}`;
		else lines.push(word);
	}
	return lines;
};
