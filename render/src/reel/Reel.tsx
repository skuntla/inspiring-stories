import React from 'react';
import {AbsoluteFill, Audio, Img, staticFile, useCurrentFrame} from 'remotion';
import {ease} from '../kit/style';

// A vertical reel from story cards (see pipeline/story/reel.py). Each card sits on a blurred copy of
// itself; the camera starts on the whole card, glides in to the illustration while the story is told,
// drifts a little, then eases back out so the card's own notes can be read before the next one.

export type ReelSlide = {id: string; from: number; frames: number; image: string; motion: 'card' | 'cover'; focus: [number, number, number]; captions?: {at: number; text: string}[];
	pages?: {from: number; to: number; speaker: string | null; words: [string, number, number][]}[]};
export type ReelTimeline = {fps: number; width: number; height: number; durationInFrames: number; audio: {src: string}; format?: 'reel' | 'short'; shots: ReelSlide[]};

const FADE = 12; // frames of cross-fade into each card
// Card boxes. A reel shows the whole card; a short keeps it clear of the platform's buttons (right
// edge) and title overlay (bottom), in the band that stays visible on every phone.
const LAYOUT = {
	reel: {left: 0, top: 240, width: 1080, height: 1440},
	short: {left: 40, top: 430, width: 900, height: 1125}, // the whole card, clear of the buttons (right) and title (bottom)
};

const clamp = (x: number) => Math.max(0, Math.min(1, x));
const between = (u: number, a: number, b: number) => ease(clamp((u - a) / (b - a)));

/** Zoom and focus drift of a slide at progress u (0..1). */
const camera = (s: ReelSlide, u: number, short: boolean) => {
	const [fx, fy, zoom] = s.focus;
	if (s.motion === 'cover') return {scale: 1 + (zoom - 1) * ease(u), fx, fy};
	if (short) return {scale: 1 + 0.09 * ease(u), fx, fy}; // the whole card, pushing in slowly
	const zin = between(u, 0.06, 0.55);
	const zout = between(u, 0.8, 0.96);
	const level = zin * (1 - zout);
	return {scale: 1 + (zoom - 1) * level, fx, fy: fy + 0.05 * between(u, 0.4, 0.85) * (1 - zout)};
};

/** A bold caption in a pill, popping in just after the card appears. */
const Caption: React.FC<{text: string; f: number; box: {left: number; top: number; width: number; height: number}}> = ({text, f, box}) => {
	const pop = clamp((f - 6) / 8);
	return (
		<div style={{position: 'absolute', left: box.left, width: box.width, top: box.top - 175, height: 150, display: 'flex', justifyContent: 'center', alignItems: 'center',
			opacity: pop, transform: `scale(${0.85 + 0.15 * ease(pop)})`}}>
			<div style={{background: 'rgba(122, 31, 31, 0.92)', color: '#fff6e0', borderRadius: 28, padding: '18px 34px', maxWidth: '88%', textAlign: 'center',
				fontFamily: '"Arial Black", "Helvetica Neue", Arial, sans-serif', fontWeight: 900, fontSize: 58, lineHeight: 1.1, textWrap: 'balance',
				boxShadow: '0 10px 30px rgba(0,0,0,0.35)', border: '4px solid #f2c14e'}}>{text}</div>
		</div>
	);
};

/** The spoken words above the card, a short page at a time, each word lighting up gold as it is
 * said. Dialogue is set in quotes. */
const WordCaptions: React.FC<{pages: NonNullable<ReelSlide['pages']>; f: number; box: {left: number; top: number; width: number}}> = ({pages, f, box}) => {
	const page = pages.find((p) => f >= p.from && f < p.to);
	if (!page) return null;
	const n = page.words.length;
	return (
		<div style={{position: 'absolute', left: box.left, width: box.width, top: box.top - 270, height: 250, display: 'flex',
			justifyContent: 'center', alignItems: 'center'}}>
			<div style={{background: 'rgba(28, 16, 10, 0.72)', borderRadius: 30, padding: '16px 30px 20px', maxWidth: '96%', textAlign: 'center',
				fontFamily: '"Arial Rounded MT Bold", "Arial Black", "Helvetica Neue", Arial, sans-serif', fontWeight: 900, fontSize: 60,
				lineHeight: 1.2, color: '#fff6e0', textWrap: 'balance', boxShadow: '0 10px 30px rgba(0,0,0,0.35)'}}>
				{page.words.map(([text, from, to], i) => {
					const on = f >= from && f < Math.max(to, from + 4);
					const said = f >= to;
					const quoted = page.speaker ? `${i === 0 ? '“' : ''}${text}${i === n - 1 ? '”' : ''}` : text;
					return (
						<React.Fragment key={i}>{i > 0 ? ' ' : ''}<span style={{color: on ? '#ffd23f' : said ? '#fff6e0' : 'rgba(255, 246, 224, 0.72)', display: 'inline-block',
							textShadow: on ? '0 0 18px rgba(255, 210, 63, 0.55)' : 'none'}}>
							{quoted}
						</span></React.Fragment>
					);
				})}
			</div>
		</div>
	);
};

const Slide: React.FC<{s: ReelSlide; f: number; opacity: number; short: boolean}> = ({s, f, opacity, short}) => {
	const {scale, fx, fy} = camera(s, clamp(f / Math.max(1, s.frames - 1)), short);
	const box = LAYOUT[short ? 'short' : 'reel'];
	const src = staticFile(s.image);
	return (
		<AbsoluteFill style={{opacity}}>
			<Img src={src} style={{position: 'absolute', width: '100%', height: '100%', objectFit: 'cover',
				filter: 'blur(38px) brightness(0.5) saturate(1.2)', transform: 'scale(1.25)'}} />
			<div style={{position: 'absolute', left: box.left, top: box.top, width: box.width, height: box.height, overflow: 'hidden',
				borderRadius: short ? 24 : 0, boxShadow: '0 20px 60px rgba(0,0,0,0.45)'}}>
				<Img src={src} style={{width: '100%', height: '100%', objectFit: 'cover',
					transformOrigin: `${(fx * 100).toFixed(2)}% ${(fy * 100).toFixed(2)}%`, transform: `scale(${scale.toFixed(4)})`}} />
			</div>
			{short && s.pages && s.pages.length > 0 && <WordCaptions pages={s.pages} f={f} box={box} />}
			{short && !(s.pages && s.pages.length) && (() => {
				const now = (s.captions ?? []).filter((c) => c.at <= f).pop();
				return now ? <Caption key={now.at} text={now.text} f={f - now.at} box={box} /> : null;
			})()}
		</AbsoluteFill>
	);
};

export const Reel: React.FC<{reel: ReelTimeline}> = ({reel}) => {
	const frame = useCurrentFrame();
	const shots = reel.shots;
	if (!shots.length) return <AbsoluteFill style={{backgroundColor: '#000'}} />;
	const i = Math.max(0, shots.findIndex((s) => frame >= s.from && frame < s.from + s.frames));
	const s = shots[i];
	const f = frame - s.from;
	const prev = i > 0 ? shots[i - 1] : undefined;
	const short = reel.format === 'short';
	return (
		<AbsoluteFill style={{backgroundColor: '#000'}}>
			{reel.audio.src && <Audio src={staticFile(reel.audio.src)} />}
			{prev && f < FADE && <Slide s={prev} f={prev.frames - 1} opacity={1} short={short} />}
			<Slide s={s} f={f} opacity={prev ? Math.min(1, f / FADE) : Math.min(1, f / 8)} short={short} />
		</AbsoluteFill>
	);
};
