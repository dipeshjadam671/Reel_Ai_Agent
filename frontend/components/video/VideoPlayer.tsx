"use client";

import React, { useRef, useState, useEffect } from "react";
import {
  Play,
  Pause,
  Volume2,
  VolumeX,
  Maximize2,
  RotateCcw,
  Sparkles,
  AlertCircle,
  Loader2,
} from "lucide-react";

interface VideoPlayerProps {
  src?: string;
  poster?: string;
  title?: string;
  captionsUrl?: string;
  resolution?: string;
  duration?: number;
  autoPlay?: boolean;
}

export function VideoPlayer({
  src,
  poster,
  title,
  captionsUrl,
  resolution = "1080x1920",
  duration = 0,
  autoPlay = false,
}: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [totalDuration, setTotalDuration] = useState(duration);
  const [isBuffering, setIsBuffering] = useState(false);
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const onPlay = () => {
      setIsPlaying(true);
      setIsBuffering(false);
      setHasError(false);
    };
    const onPause = () => setIsPlaying(false);
    const onTimeUpdate = () => setCurrentTime(video.currentTime);
    const onLoadedMetadata = () => {
      if (video.duration) setTotalDuration(video.duration);
      setHasError(false);
    };
    const onWaiting = () => setIsBuffering(true);
    const onPlaying = () => {
      setIsBuffering(false);
      setIsPlaying(true);
    };
    const onCanPlay = () => {
      setIsBuffering(false);
      setHasError(false);
    };
    const onError = () => {
      console.warn("Video stream loading or interrupted, will retry on play");
      setIsBuffering(false);
      setHasError(true);
    };

    video.addEventListener("play", onPlay);
    video.addEventListener("pause", onPause);
    video.addEventListener("timeupdate", onTimeUpdate);
    video.addEventListener("loadedmetadata", onLoadedMetadata);
    video.addEventListener("waiting", onWaiting);
    video.addEventListener("playing", onPlaying);
    video.addEventListener("canplay", onCanPlay);
    video.addEventListener("error", onError);

    return () => {
      video.removeEventListener("play", onPlay);
      video.removeEventListener("pause", onPause);
      video.removeEventListener("timeupdate", onTimeUpdate);
      video.removeEventListener("loadedmetadata", onLoadedMetadata);
      video.removeEventListener("waiting", onWaiting);
      video.removeEventListener("playing", onPlaying);
      video.removeEventListener("canplay", onCanPlay);
      video.removeEventListener("error", onError);
    };
  }, [src]);

  const togglePlay = async () => {
    const video = videoRef.current;
    if (!video) return;
    if (isPlaying) {
      video.pause();
    } else {
      setIsBuffering(true);
      try {
        await video.play();
        setIsPlaying(true);
        setIsBuffering(false);
        setHasError(false);
      } catch (err: any) {
        console.warn("Play interrupted or stream re-establishing, retrying with fallback...", err);
        try {
          if (err?.name === "NotAllowedError") {
            video.muted = true;
            setIsMuted(true);
          } else {
            video.load();
          }
          await video.play();
          setIsPlaying(true);
          setIsBuffering(false);
          setHasError(false);
        } catch (retryErr) {
          console.error("Playback failed after retry:", retryErr);
          setIsBuffering(false);
          setHasError(true);
        }
      }
    }
  };

  const toggleMute = () => {
    if (!videoRef.current) return;
    videoRef.current.muted = !isMuted;
    setIsMuted(!isMuted);
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!videoRef.current) return;
    const seekTime = parseFloat(e.target.value);
    videoRef.current.currentTime = seekTime;
    setCurrentTime(seekTime);
  };

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m}:${s < 10 ? "0" : ""}${s}`;
  };

  const toggleFullscreen = () => {
    if (!videoRef.current) return;
    if (videoRef.current.requestFullscreen) {
      videoRef.current.requestFullscreen();
    }
  };

  return (
    <div className="relative group w-full max-w-[340px] aspect-[9/16] bg-black rounded-2xl overflow-hidden shadow-2xl border border-slate-800 flex flex-col justify-between">
      {/* Top Overlay Badge */}
      <div className="absolute top-3 left-3 right-3 flex items-center justify-between z-20 pointer-events-none">
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-black/60 backdrop-blur-md border border-white/10 text-[10px] font-semibold text-slate-200">
          <Sparkles className="w-3 h-3 text-emerald-400" />
          <span>{resolution} • Vertical (9:16)</span>
        </div>
      </div>

      {/* Main Video Element */}
      {src ? (
        <video
          ref={videoRef}
          src={src}
          poster={poster}
          playsInline
          loop
          preload="auto"
          crossOrigin="anonymous"
          autoPlay={autoPlay}
          muted={isMuted}
          onClick={togglePlay}
          className="w-full h-full object-cover cursor-pointer"
        />
      ) : (
        <div className="w-full h-full flex flex-col items-center justify-center p-6 text-center bg-slate-900/80">
          <RotateCcw className="w-10 h-10 text-emerald-400 animate-spin mb-3" />
          <p className="text-sm font-semibold text-slate-200">Video Render in Progress</p>
          <p className="text-xs text-slate-400 mt-1">
            Agents are composing vertical scenes, voiceover, and visual effects...
          </p>
        </div>
      )}

      {/* Center Play Button Overlay */}
      {src && !isPlaying && (
        <button
          onClick={togglePlay}
          className="absolute inset-0 m-auto w-16 h-16 rounded-full bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 flex items-center justify-center shadow-xl shadow-emerald-500/30 transition transform hover:scale-110 active:scale-95 z-20 backdrop-blur-sm"
        >
          {isBuffering ? (
            <Loader2 className="w-7 h-7 text-slate-950 animate-spin" />
          ) : (
            <Play className="w-7 h-7 fill-slate-950 ml-1 text-slate-950" />
          )}
        </button>
      )}

      {/* Bottom Controls Bar */}
      {src && (
        <div className="absolute bottom-0 left-0 right-0 p-3 bg-gradient-to-t from-black/90 via-black/50 to-transparent z-20 opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex flex-col gap-2">
          {/* Progress Bar */}
          <input
            type="range"
            min={0}
            max={totalDuration || 100}
            step={0.1}
            value={currentTime}
            onChange={handleSeek}
            className="w-full h-1 bg-slate-700/80 rounded-lg appearance-none cursor-pointer accent-emerald-400"
          />

          <div className="flex items-center justify-between text-xs text-white">
            <div className="flex items-center gap-3">
              <button onClick={togglePlay} className="hover:text-emerald-400 transition">
                {isPlaying ? <Pause className="w-4 h-4 fill-white" /> : <Play className="w-4 h-4 fill-white" />}
              </button>

              <button onClick={toggleMute} className="hover:text-emerald-400 transition">
                {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
              </button>

              <span className="text-[11px] font-mono text-slate-300">
                {formatTime(currentTime)} / {formatTime(totalDuration)}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <button onClick={toggleFullscreen} className="hover:text-emerald-400 transition">
                <Maximize2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
