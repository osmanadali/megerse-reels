// public/reels/<id>/reel.json biçimi
export type Word = {text: string; startMs: number; endMs: number};

export type Scene = {
  durationSec: number;
  bg: string; // arka plan rengi
  images: {src: string; x: number; y: number; size: number; motion?: 'float' | 'zoom' | 'pop'}[];
  title?: string; // sahne üstü kısa etiket (altyazıyla aynı bilgiyi tekrar etme)
};

export type Reel = {
  id: string;
  badge: string; // üst rozet
  audio?: string; // public altındaki ses dosyası
  scenes: Scene[];
  words: Word[];
  sources: string[]; // kaynakça kartı
};
