import {Config} from '@remotion/cli/config';

// Bulut ortamında hazır Chromium; kendi bilgisayarında bu satır gerekmez (Remotion kendi indirir).
if (process.env.REMOTION_CHROME) {
  Config.setBrowserExecutable(process.env.REMOTION_CHROME);
}
Config.setVideoImageFormat('jpeg');
Config.setCodec('h264');
Config.setCrf(18);
