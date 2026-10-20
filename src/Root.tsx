import {Composition, staticFile} from 'remotion';
import {Reel as ReelComp, reelDurationFrames} from './Reel';
import type {Reel} from './types';

const FPS = 30;

export const RemotionRoot = () => (
  <Composition
    id="Reel"
    component={ReelComp}
    width={1080}
    height={1920}
    fps={FPS}
    durationInFrames={1}
    defaultProps={{reelId: 'demo', reel: null as Reel | null}}
    calculateMetadata={async ({props}) => {
      const res = await fetch(staticFile(`reels/${props.reelId}/reel.json`));
      const reel: Reel = await res.json();
      return {props: {...props, reel}, durationInFrames: reelDurationFrames(reel, FPS)};
    }}
  />
);
