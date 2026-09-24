import {makeHuman} from '../../../kit/human';
import type {Rig} from '../../../kit/types';

// A village man (the loudest of the mockers): a white head-cloth turban, a thin mustache, a rust
// shirt with rolled sleeves and a white dhoti.
export const rig: Rig = {
	id: 'villager',
	stances: ['stand', 'walk', 'sit', 'reach', 'hold'],
	moods: ['neutral', 'happy', 'sad', 'surprised', 'worried', 'scared', 'angry', 'thoughtful', 'proud', 'tired', 'calm'],
	height: 490,
	anchors: {hand: [90, -262], head: [8, -522]},
	Component: makeHuman({
		skin: '#9a6443', skinShade: '#7e4f33',
		turban: {color: '#f1ece0', shade: '#d8d0bc'}, mustache: {color: '#2a1d16'}, brows: '#2a1d16',
		shirt: '#a35d3a', shirtShade: '#874b2e', sleeves: 'rolled',
		skirt: {color: '#f7f3ea', shade: '#d8d0bc', hem: -95},
		pants: '#9a6443', shoes: '#5a3a24',
	}),
};
