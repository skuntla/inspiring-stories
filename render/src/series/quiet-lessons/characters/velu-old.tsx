import {makeHuman} from '../../../kit/human';
import type {Rig} from '../../../kit/types';

// Velu, old: the same man forty years on; white hair and mustache, lined face, a slight stoop, a cream
// long-sleeved kurta over the white dhoti, and the same mustard towel over his shoulder.
export const rig: Rig = {
	id: 'velu-old',
	stances: ['stand', 'walk', 'sit', 'reach', 'hold', 'dig'],
	moods: ['neutral', 'happy', 'sad', 'surprised', 'worried', 'scared', 'angry', 'thoughtful', 'proud', 'tired', 'calm'],
	height: 465,
	anchors: {hand: [90, -262], head: [8, -482]},
	Component: makeHuman({
		skin: '#8d5a3b', skinShade: '#744831',
		hair: {color: '#eeeae2', style: 'fringe'}, mustache: {color: '#eeeae2'}, brows: '#eeeae2', browWidth: 6, wrinkles: true,
		shirt: '#efe6d2', shirtShade: '#d8ccb2', sleeves: 'long',
		skirt: {color: '#f7f3ea', shade: '#d8d0bc', hem: -95}, robe: {sash: '#c9a13b'},
		pants: '#8d5a3b', shoes: '#5a3a24', stoop: 5,
	}),
};
