/**
 * TTS 工具 — 基于 Web Speech API
 * 用法：
 *   import { speak, stopSpeaking, isSpeaking } from '@/utils/tts.js'
 *   speak('你好，这是一段播报文字')
 *   stopSpeaking()
 */

import { ref } from 'vue';

export const isSpeaking = ref(false);

let currentUtterance = null;

export function speak(text, options = {}) {
  if (!window.speechSynthesis) {
    console.warn('当前浏览器不支持 Web Speech API');
    return;
  }
  stopSpeaking();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = options.lang || 'zh-CN';
  utterance.rate = options.rate || 1.0;
  utterance.pitch = options.pitch || 1.0;
  utterance.volume = options.volume || 1.0;

  // 优先选择中文语音
  const voices = window.speechSynthesis.getVoices();
  const zhVoice = voices.find(v => v.lang.startsWith('zh'));
  if (zhVoice) utterance.voice = zhVoice;

  utterance.onstart = () => { isSpeaking.value = true; };
  utterance.onend = () => { isSpeaking.value = false; currentUtterance = null; };
  utterance.onerror = () => { isSpeaking.value = false; currentUtterance = null; };

  currentUtterance = utterance;
  window.speechSynthesis.speak(utterance);
}

export function stopSpeaking() {
  if (window.speechSynthesis) {
    window.speechSynthesis.cancel();
  }
  isSpeaking.value = false;
  currentUtterance = null;
}

export function toggleSpeak(text, options = {}) {
  if (isSpeaking.value) {
    stopSpeaking();
  } else {
    speak(text, options);
  }
}
