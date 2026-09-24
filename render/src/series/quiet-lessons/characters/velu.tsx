import {makeHuman} from '../../../kit/human';
import type {Rig} from '../../../kit/types';

// Velu, young: a lean, sun-darkened villager of about thirty; short black hair and a black mustache,
// a white sleeveless vest, a white dhoti to mid-shin and a mustard towel over one shoulder. Digs.
export const rig: Rig = {
	id: 'velu',
	stances: ['stand', 'walk', 'sit', 'reach', 'hold', 'dig'],
	moods: ['neutral', 'happy', 'sad', 'surprised', 'worried', 'scared', 'angry', 'thoughtful', 'proud', 'tired', 'calm'],
	height: 470,
	anchors: {hand: [90, -262], head: [8, -482]},
	Component: makeHuman({
		skin: '#8d5a3b', skinShade: '#744831',
		hair: {color: '#1f1814'}, mustache: {color: '#1f1814'}, brows: '#1f1814',
		shirt: '#f1ece0', shirtShade: '#d8d0bc', sleeves: 'none',
		skirt: {color: '#f7f3ea', shade: '#d8d0bc', hem: -95}, robe: {sash: '#c9a13b'},
		pants: '#8d5a3b', shoes: '#5a3a24',
	}),
};
