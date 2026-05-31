package com.clipforge.presentation.navigation

sealed class Screen(val route: String) {
    object Splash : Screen("splash")
    object Login : Screen("login")
    object Register : Screen("register")
    object Home : Screen("home")
    object ImportVideo : Screen("import_video")
    object AIClips : Screen("ai_clips")
    object Projects : Screen("projects")
    object Settings : Screen("settings")
    object Subscription : Screen("subscription")
    
    // Video & Clip Flow
    object VideoMetadataPreview : Screen("video_metadata_preview/{videoId}") {
        fun createRoute(videoId: String) = "video_metadata_preview/$videoId"
    }
    object ClipOptions : Screen("clip_options/{videoId}") {
        fun createRoute(videoId: String) = "clip_options/$videoId"
    }
    object ManualClip : Screen("manual_clip/{videoId}") {
        fun createRoute(videoId: String) = "manual_clip/$videoId"
    }
    object ClipDetail : Screen("clip_detail/{clipId}") {
        fun createRoute(clipId: String) = "clip_detail/$clipId"
    }

    // AI Features
    object AIHighlight : Screen("ai_highlight/{videoId}") {
        fun createRoute(videoId: String) = "ai_highlight/$videoId"
    }
    object SpeechSearch : Screen("speech_search/{videoId}") {
        fun createRoute(videoId: String) = "speech_search/$videoId"
    }
    object SceneDetection : Screen("scene_detection/{videoId}") {
        fun createRoute(videoId: String) = "scene_detection/$videoId"
    }
    object ObjectTracking : Screen("object_tracking/{videoId}") {
        fun createRoute(videoId: String) = "object_tracking/$videoId"
    }
    object FaceTracking : Screen("face_tracking/{videoId}") {
        fun createRoute(videoId: String) = "face_tracking/$videoId"
    }
    object GestureTracking : Screen("gesture_tracking/{videoId}") {
        fun createRoute(videoId: String) = "gesture_tracking/$videoId"
    }
    object ShortsGenerator : Screen("shorts_generator/{clipId}") {
        fun createRoute(clipId: String) = "shorts_generator/$clipId"
    }
}
