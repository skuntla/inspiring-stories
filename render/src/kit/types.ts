import type React from 'react';

// ---- story-timeline/v1 (written by `story timeline`) ------------------------------------

export type Shape = 'rest' | 'closed' | 'fv' | 'consonant' | 'ee' | 'mid' | 'open' | 'round';
export type Facing = 'left' | 'right' | 'camera' | 'away';
export type TimeOfDay = 'dawn' | 'morning' | 'midday' | 'afternoon' | 'dusk' | 'night';
export type View = [number, number, number]; // center x, center y, zoom

export type CastMember = {
	id: string;
	x: number;
	depth: number; // 1 foreground, 0.6 background
	facing: Facing;
	stance: string;
	mood: string;
	mouth: [number, Shape][]; // [frame within shot, shape]
	blinks: number[]; // frames within shot
	travel?: {from: number; to: number; speed: number}; // walking left/right across the shot
};

export type CaptionPage = {
	from: number;
	to: number;
	speaker: string | null;
	words: [string, number, number][];
};

export type Shot = {
	id: string;
	from: number;
	frames: number;
	location: string;
	timeOfDay: TimeOfDay;
	atmosphere: string[];
	ambience: string;
	props: string[];
	camera: {
		framing: 'wide' | 'medium' | 'close';
		subject?: {id: string; x: number; depth: number; facing: Facing};
		from: View; // [dx, dy, zoom factor] from the shot's base view
		to: View;
		ease: string;
	};
	cast: CastMember[];
	captions: CaptionPage[];
};

export type Timeline = {
	schema: 'story-timeline/v1';
	fps: number;
	width: number;
	height: number;
	durationInFrames: number;
	series: string;
	episode: string;
	title: string;
	audio: {src: string; music?: string};
	shots: Shot[];
};

// ---- component library -----------------------------------------------------------------------

export type Palette = {
	skyTop: string;
	skyMid: string;
	skyBottom: string;
	sun: string;
	sunX: number;
	sunY: number;
	tint: string; // laid over the whole scene
	tintOpacity: number;
	light: number; // 0 (night) .. 1 (midday), for components that want to dim themselves
};

/** Everything a component may use to draw: seconds since the shot started, and the shot's light. */
/** A word spoken in the current shot, in seconds from the shot's start; `speaker` is null for the narrator. */
export type SpokenWord = {text: string; from: number; to: number; speaker: string | null};

/** What every component draws from: the shot's clock, light, and the words spoken in it (so text
 * shots and inserts can time themselves to the voice instead of hard-coded seconds). */
export type DrawContext = {t: number; palette: Palette; timeOfDay: TimeOfDay; words?: SpokenWord[]};

export type RigProps = DrawContext & {
	stance: string;
	mood: string;
	mouth: Shape;
	eye: number; // 1 open .. 0 closed
	speaking: boolean;
	facing: Facing;
	walkSpeed?: number; // px/s in the rig's own units while walking (0 = on the spot)
};

/** A character rig, drawn facing right with its origin at the feet on the ground line. */
export type Rig = {
	id: string;
	stances: string[];
	moods: string[];
	height: number; // approximate standing height in px at depth 1
	anchors: {hand: [number, number]; head: [number, number]};
	Component: React.FC<RigProps>;
};

/** A location: characters are drawn between Background and Foreground. */
export type Location = {
	id: string;
	groundY: number; // ground line for depth-1 characters, in scene px (1920x1080)
	backgroundGroundY?: number; // ground line for background (depth 0.6) characters
	interior?: boolean; // interiors ignore the sky
	showsText?: boolean; // the location draws its own text (a page, a quote card): captions are hidden
	propSlots: [number, number][]; // where free props stand, in order
	Background: React.FC<DrawContext>;
	Foreground?: React.FC<DrawContext>;
};

export type Prop = {
	id: string;
	width: number;
	Component: React.FC<DrawContext>; // drawn with its origin at the bottom center
};

/** The components one render needs; written to src/generated/registry.ts by `story render`. */
export type Registry = {
	characters: Record<string, Rig>;
	locations: Record<string, Location>;
	props: Record<string, Prop>;
};
