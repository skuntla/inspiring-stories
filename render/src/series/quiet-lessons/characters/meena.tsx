import {makeHuman} from '../../../kit/human';
import type {Rig} from '../../../kit/types';

// Meena, a girl of about eight: a long braid with a red ribbon, a green blouse and a long mustard
// pavadai skirt; child proportions (small body, big head).
export const rig: Rig = {
	id: 'meena',
	stances: ['stand', 'walk', 'sit', 'reach', 'hold'],
	moods: ['neutral', 'happy', 'sad', 'surprised', 'worried', 'scared', 'angry', 'thoughtful', 'proud', 'tired', 'calm'],
	height: 360,
	anchors: {hand: [65, -190], head: [6, -360]},
	Component: makeHuman({
		skin: '#a86f48', skinShade: '#8c5a3a',
		hair: {color: '#1f1814', style: 'braids', ribbon: '#c8323a'}, brows: '#1f1814',
		shirt: '#4f9a5a', shirtShade: '#3f8049', sleeves: 'rolled',
		skirt: {color: '#e0a33a', shade: '#c4862a', hem: -40},
		pants: '#a86f48', shoes: '#8a5a2e', size: 0.72, headScale: 1.2,
	}),
};
