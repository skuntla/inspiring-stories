import React from 'react';
import type {CaptionPage} from './types';

/** Word-level captions sized for phones: one page (at most two short lines), the spoken word
 * highlighted. Narration is italic, dialogue upright; speaker names are never printed. */
export const Captions: React.FC<{pages: CaptionPage[]; frame: number}> = ({pages, frame}) => {
	const page = pages.find((p) => frame >= p.from && frame < p.to);
	if (!page) return null;
	return (
		<div style={{position: 'absolute', bottom: 92, width: '100%', display: 'flex', justifyContent: 'center'}}>
			<div
				style={{
					background: 'rgba(30, 25, 18, 0.6)',
					borderRadius: 22,
					padding: '12px 34px 16px',
					maxWidth: '78%',
					textAlign: 'center',
					fontFamily: 'Georgia, "Times New Roman", serif',
					fontStyle: page.speaker ? 'normal' : 'italic',
					fontWeight: page.speaker ? 600 : 400,
					fontSize: 66,
					lineHeight: 1.18,
					color: '#f7f1e4',
					textShadow: '0 2px 6px rgba(0,0,0,0.35)',
				}}
			>
				{page.words.map(([text, from, to], i) => (
					<span key={i} style={{color: frame >= from && frame < to ? '#ffd98a' : '#f7f1e4'}}>
						{text}
						{i < page.words.length - 1 ? ' ' : ''}
					</span>
				))}
			</div>
		</div>
	);
};
