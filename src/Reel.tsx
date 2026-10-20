import {createTikTokStyleCaptions} from '@remotion/captions';
import {fade} from '@remotion/transitions/fade';
import {slide} from '@remotion/transitions/slide';
import {linearTiming, TransitionSeries} from '@remotion/transitions';
import {
  AbsoluteFill,
  Audio,
  Img,
  interpolate,
  Sequence,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import type {Reel as ReelData, Scene} from './types';

const FONT = 'Montserrat';
const TRANSITION = 8; // kare
const SOURCES_SEC = 3;

const fontCss = `
@font-face{font-family:${FONT};font-weight:800;src:url(${staticFile('montserrat-latin-ext-800-normal.woff2')}) format('woff2');
unicode-range:U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF;}
@font-face{font-family:${FONT};font-weight:800;src:url(${staticFile('montserrat-latin-800-normal.woff2')}) format('woff2');}
`;

export const reelDurationFrames = (reel: ReelData, fps: number) =>
  reel.scenes.reduce((s, sc) => s + Math.round(sc.durationSec * fps), 0) -
  TRANSITION * (reel.scenes.length - 1) +
  SOURCES_SEC * fps;

const SceneView: React.FC<{scene: Scene; reelId: string}> = ({scene, reelId}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <AbsoluteFill style={{background: scene.bg}}>
      {scene.images.map((im, i) => {
        const pop = spring({frame: frame - i * 6, fps, config: {damping: 12}});
        const t = frame / fps;
        const scale =
          im.motion === 'zoom' ? 1 + t * 0.04 : im.motion === 'pop' ? pop : 1;
        const dy = im.motion === 'float' ? Math.sin(t * 2 + i) * 18 : 0;
        return (
          <Img
            key={i}
            src={staticFile(`reels/${reelId}/${im.src}`)}
            style={{
              position: 'absolute',
              left: im.x - im.size / 2,
              top: im.y - im.size / 2 + dy,
              width: im.size,
              height: im.size,
              transform: `scale(${scale})`,
            }}
          />
        );
      })}
      {scene.title && (
        <div
          style={{
            position: 'absolute', top: 330, width: '100%', textAlign: 'center',
            fontFamily: FONT, fontWeight: 800, fontSize: 64, color: 'white',
            textShadow: '0 4px 16px rgba(0,0,0,.45)',
          }}
        >
          {scene.title}
        </div>
      )}
    </AbsoluteFill>
  );
};

// Kelime kelime vurgulu altyazı
const Captions: React.FC<{reel: ReelData}> = ({reel}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const ms = (frame / fps) * 1000;
  const {pages} = createTikTokStyleCaptions({
    captions: reel.words.map((w) => ({
      text: ' ' + w.text, startMs: w.startMs, endMs: w.endMs, timestampMs: w.startMs, confidence: 1,
    })),
    combineTokensWithinMilliseconds: 900,
  });
  const page = pages.find((p) => ms >= p.startMs && ms < p.startMs + p.durationMs);
  if (!page) return null;
  return (
    <div
      style={{
        position: 'absolute', bottom: 430, width: '100%', padding: '0 80px', textAlign: 'center',
        fontFamily: FONT, fontWeight: 800, fontSize: 76, lineHeight: 1.15, color: 'white',
        WebkitTextStroke: '3px black', paintOrder: 'stroke',
      }}
    >
      {page.tokens.map((t, i) => {
        const active = ms >= t.fromMs && ms < t.toMs;
        return (
          <span key={i} style={{color: active ? '#FFD23F' : 'white'}}>
            {t.text}
          </span>
        );
      })}
    </div>
  );
};

const Badge: React.FC<{text: string}> = ({text}) => (
  <div
    style={{
      position: 'absolute', top: 170, left: '50%', transform: 'translateX(-50%)',
      background: '#E63946', color: 'white', padding: '14px 34px', borderRadius: 40,
      fontFamily: FONT, fontWeight: 800, fontSize: 40, letterSpacing: 1,
    }}
  >
    {text}
  </div>
);

const Sources: React.FC<{sources: string[]}> = ({sources}) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill
      style={{
        background: '#1D3557', justifyContent: 'center', padding: 90,
        opacity: interpolate(frame, [0, 10], [0, 1], {extrapolateRight: 'clamp'}),
        fontFamily: FONT, fontWeight: 800, color: 'white',
      }}
    >
      <div style={{fontSize: 60, marginBottom: 40}}>Kaynakça</div>
      {sources.map((s, i) => (
        <div key={i} style={{fontSize: 34, marginBottom: 18, opacity: 0.9}}>• {s}</div>
      ))}
    </AbsoluteFill>
  );
};

export const Reel: React.FC<{reelId: string; reel: ReelData | null}> = ({reelId, reel}) => {
  const {fps, durationInFrames} = useVideoConfig();
  if (!reel) return null;
  const mainFrames = durationInFrames - SOURCES_SEC * fps;
  return (
    <AbsoluteFill style={{background: 'black'}}>
      <style>{fontCss}</style>
      <TransitionSeries>
        {reel.scenes.flatMap((sc, i) => [
          <TransitionSeries.Sequence key={`s${i}`} durationInFrames={Math.round(sc.durationSec * fps)}>
            <SceneView scene={sc} reelId={reelId} />
          </TransitionSeries.Sequence>,
          ...(i < reel.scenes.length - 1
            ? [
                <TransitionSeries.Transition
                  key={`t${i}`}
                  presentation={i % 2 ? fade() : slide({direction: 'from-right'})}
                  timing={linearTiming({durationInFrames: TRANSITION})}
                />,
              ]
            : []),
        ])}
      </TransitionSeries>
      <Sequence durationInFrames={mainFrames}>
        <Badge text={reel.badge} />
        <Captions reel={reel} />
      </Sequence>
      <Sequence from={mainFrames}>
        <Sources sources={reel.sources} />
      </Sequence>
      {reel.audio && <Audio src={staticFile(`reels/${reelId}/${reel.audio}`)} />}
    </AbsoluteFill>
  );
};
