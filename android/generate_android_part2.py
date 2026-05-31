import os

files = {
    # Updates to Navigation
    "app/src/main/java/com/clipforge/presentation/navigation/Screen.kt": """package com.clipforge.presentation.navigation

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
""",
    
    "app/src/main/java/com/clipforge/presentation/navigation/AppNavGraph.kt": """package com.clipforge.presentation.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.clipforge.presentation.component.BottomNavigationBar
import com.clipforge.presentation.screen.auth.LoginScreen
import com.clipforge.presentation.screen.auth.RegisterScreen
import com.clipforge.presentation.screen.auth.SplashScreen
import com.clipforge.presentation.screen.clips.AIClipsScreen
import com.clipforge.presentation.screen.home.HomeScreen
import com.clipforge.presentation.screen.importvideo.ImportVideoScreen
import com.clipforge.presentation.screen.projects.ProjectsScreen
import com.clipforge.presentation.screen.settings.SettingsScreen
import com.clipforge.presentation.screen.subscription.SubscriptionScreen
import com.clipforge.presentation.screen.clips.ClipDetailScreen
import com.clipforge.presentation.screen.importvideo.VideoMetadataPreviewScreen
import com.clipforge.presentation.screen.importvideo.ClipOptionsScreen
import com.clipforge.presentation.screen.clips.ManualClipScreen
import com.clipforge.presentation.screen.features.*

@Composable
fun AppNavGraph() {
    val navController = rememberNavController()
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route

    val showBottomNav = currentRoute in listOf(
        Screen.Home.route,
        Screen.AIClips.route,
        Screen.Projects.route,
        Screen.Settings.route
    )

    Scaffold(
        bottomBar = {
            if (showBottomNav) {
                BottomNavigationBar(navController = navController, currentRoute = currentRoute)
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = Screen.Splash.route,
            modifier = Modifier.padding(innerPadding)
        ) {
            composable(Screen.Splash.route) { SplashScreen(navController) }
            composable(Screen.Login.route) { LoginScreen(navController) }
            composable(Screen.Register.route) { RegisterScreen(navController) }
            composable(Screen.Home.route) { HomeScreen(navController) }
            composable(Screen.ImportVideo.route) { ImportVideoScreen(navController) }
            composable(Screen.AIClips.route) { AIClipsScreen(navController) }
            composable(Screen.Projects.route) { ProjectsScreen(navController) }
            composable(Screen.Settings.route) { SettingsScreen(navController) }
            composable(Screen.Subscription.route) { SubscriptionScreen(navController) }
            
            // Sub-flows
            composable(Screen.VideoMetadataPreview.route) { VideoMetadataPreviewScreen(navController) }
            composable(Screen.ClipOptions.route) { ClipOptionsScreen(navController) }
            composable(Screen.ManualClip.route) { ManualClipScreen(navController) }
            composable(Screen.ClipDetail.route) { ClipDetailScreen(navController) }
            
            // AI Features
            composable(Screen.AIHighlight.route) { AIHighlightScreen(navController) }
            composable(Screen.SpeechSearch.route) { SpeechSearchScreen(navController) }
            composable(Screen.SceneDetection.route) { SceneDetectionScreen(navController) }
            composable(Screen.ObjectTracking.route) { ObjectTrackingScreen(navController) }
            composable(Screen.FaceTracking.route) { FaceTrackingScreen(navController) }
            composable(Screen.GestureTracking.route) { GestureTrackingScreen(navController) }
            composable(Screen.ShortsGenerator.route) { ShortsGeneratorScreen(navController) }
        }
    }
}
""",

    # Video Metadata & Clip Options
    "app/src/main/java/com/clipforge/presentation/screen/importvideo/VideoMetadataPreviewScreen.kt": """package com.clipforge.presentation.screen.importvideo

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.clipforge.presentation.navigation.Screen

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun VideoMetadataPreviewScreen(navController: NavController) {
    Scaffold(
        topBar = { TopAppBar(title = { Text("Preview Video") }) }
    ) { padding ->
        Column(modifier = Modifier.padding(padding).padding(16.dp)) {
            Card(modifier = Modifier.fillMaxWidth().height(200.dp)) {
                // Placeholder for Video Thumbnail
            }
            Spacer(modifier = Modifier.height(16.dp))
            Text("Video Title", style = MaterialTheme.typography.titleLarge)
            Text("Channel Name • 03:32 • 1080p", style = MaterialTheme.typography.bodyMedium)
            
            Spacer(modifier = Modifier.height(32.dp))
            Button(onClick = { navController.navigate(Screen.ClipOptions.createRoute("sample_video_id")) }, modifier = Modifier.fillMaxWidth()) {
                Text("Import & Choose Action")
            }
            Spacer(modifier = Modifier.height(8.dp))
            OutlinedButton(onClick = { navController.popBackStack() }, modifier = Modifier.fillMaxWidth()) {
                Text("Cancel")
            }
        }
    }
}
""",

    "app/src/main/java/com/clipforge/presentation/screen/importvideo/ClipOptionsScreen.kt": """package com.clipforge.presentation.screen.importvideo

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.clipforge.presentation.component.PremiumGateDialog
import com.clipforge.presentation.navigation.Screen

data class ActionItem(val title: String, val desc: String, val route: String, val isPremium: Boolean)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ClipOptionsScreen(navController: NavController) {
    var showPremiumDialog by remember { mutableStateOf(false) }
    var selectedPremiumFeature by remember { mutableStateOf("") }
    
    val actions = listOf(
        ActionItem("Manual Clip", "Cut video manually", Screen.ManualClip.createRoute("vid"), false),
        ActionItem("AI Highlight", "Detect best moments", Screen.AIHighlight.createRoute("vid"), false),
        ActionItem("Scene Detection", "Detect scene changes", Screen.SceneDetection.createRoute("vid"), false),
        ActionItem("Speech Search", "Search by spoken words", Screen.SpeechSearch.createRoute("vid"), true),
        ActionItem("Object Tracking", "Track objects like cars, people", Screen.ObjectTracking.createRoute("vid"), true),
        ActionItem("Face Tracking", "Auto clip when face appears", Screen.FaceTracking.createRoute("vid"), true),
        ActionItem("Gesture Tracking", "Track hand gestures", Screen.GestureTracking.createRoute("vid"), true),
        ActionItem("Shorts Generator", "Make TikTok/Reels automatically", Screen.ShortsGenerator.createRoute("clip"), true)
    )

    if (showPremiumDialog) {
        PremiumGateDialog(
            featureName = selectedPremiumFeature,
            onDismiss = { showPremiumDialog = false },
            onUpgrade = { 
                showPremiumDialog = false
                navController.navigate(Screen.Subscription.route) 
            }
        )
    }

    Scaffold(
        topBar = { TopAppBar(title = { Text("Choose Action") }) }
    ) { padding ->
        LazyColumn(modifier = Modifier.padding(padding).padding(16.dp)) {
            items(actions) { action ->
                Card(
                    modifier = Modifier.fillMaxWidth().padding(bottom = 12.dp),
                    onClick = {
                        if (action.isPremium) {
                            // TODO: Check real user subscription state
                            selectedPremiumFeature = action.title
                            showPremiumDialog = true
                        } else {
                            navController.navigate(action.route)
                        }
                    }
                ) {
                    Row(modifier = Modifier.padding(16.dp).fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        Column {
                            Text(action.title, style = MaterialTheme.typography.titleMedium)
                            Text(action.desc, style = MaterialTheme.typography.bodySmall)
                        }
                        if (action.isPremium) {
                            Icon(Icons.Default.Lock, contentDescription = "Premium")
                        }
                    }
                }
            }
        }
    }
}
""",

    # Dialogs & Bottom Sheets
    "app/src/main/java/com/clipforge/presentation/component/PremiumGateDialog.kt": """package com.clipforge.presentation.component

import androidx.compose.material3.*
import androidx.compose.runtime.Composable

@Composable
fun PremiumGateDialog(featureName: String, onDismiss: () -> Unit, onUpgrade: () -> Unit) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("⭐ Premium Feature") },
        text = { 
            Text("$featureName is available in ClipForge Premium.\\n\\n✓ Unlimited videos\\n✓ 4K Export\\n✓ No Watermark\\n✓ All AI Tracking Features")
        },
        confirmButton = {
            Button(onClick = onUpgrade) {
                Text("Upgrade Now")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Later")
            }
        }
    )
}
""",

    "app/src/main/java/com/clipforge/presentation/component/DailyLimitDialog.kt": """package com.clipforge.presentation.component

import androidx.compose.material3.*
import androidx.compose.runtime.Composable

@Composable
fun DailyLimitDialog(onDismiss: () -> Unit, onUpgrade: () -> Unit) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("🔒 Daily Limit Reached") },
        text = { 
            Text("You have imported 3/3 videos today.\\nResets at 00:00.\\n\\nUpgrade to Premium for unlimited imports.")
        },
        confirmButton = {
            Button(onClick = onUpgrade) {
                Text("Upgrade Premium")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Come back tomorrow")
            }
        }
    )
}
""",

    "app/src/main/java/com/clipforge/presentation/component/JobProgressBottomSheet.kt": """package com.clipforge.presentation.component

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun JobProgressBottomSheet(
    jobName: String,
    progress: Float,
    statusMessage: String,
    onCancel: () -> Unit,
    onDismissRequest: () -> Unit
) {
    ModalBottomSheet(onDismissRequest = onDismissRequest) {
        Column(modifier = Modifier.padding(24.dp).fillMaxWidth()) {
            Text("🔄 $jobName", style = MaterialTheme.typography.titleMedium)
            Spacer(modifier = Modifier.height(16.dp))
            LinearProgressIndicator(progress = progress, modifier = Modifier.fillMaxWidth())
            Spacer(modifier = Modifier.height(8.dp))
            Text(statusMessage, style = MaterialTheme.typography.bodyMedium)
            Spacer(modifier = Modifier.height(24.dp))
            OutlinedButton(onClick = onCancel, modifier = Modifier.fillMaxWidth()) {
                Text("Cancel")
            }
            Spacer(modifier = Modifier.height(24.dp))
        }
    }
}
""",

    # Screen: Manual Clip & Detail
    "app/src/main/java/com/clipforge/presentation/screen/clips/ManualClipScreen.kt": """package com.clipforge.presentation.screen.clips

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.clipforge.presentation.navigation.Screen

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ManualClipScreen(navController: NavController) {
    var title by remember { mutableStateOf("") }
    
    Scaffold(
        topBar = { TopAppBar(title = { Text("Manual Clip") }) }
    ) { padding ->
        Column(modifier = Modifier.padding(padding).padding(16.dp)) {
            Card(modifier = Modifier.fillMaxWidth().height(200.dp)) {
                // Video Player Placeholder
            }
            Spacer(modifier = Modifier.height(16.dp))
            Text("Start Time: 00:00:30")
            Text("End Time: 00:01:30")
            Text("Duration: 1 min 0 sec")
            Spacer(modifier = Modifier.height(16.dp))
            OutlinedTextField(
                value = title,
                onValueChange = { title = it },
                label = { Text("Clip Title (optional)") },
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(modifier = Modifier.height(24.dp))
            Button(onClick = { navController.navigate(Screen.ClipDetail.createRoute("new_clip")) }, modifier = Modifier.fillMaxWidth()) {
                Text("Create Clip")
            }
        }
    }
}
""",

    "app/src/main/java/com/clipforge/presentation/screen/clips/ClipDetailScreen.kt": """package com.clipforge.presentation.screen.clips

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ClipDetailScreen(navController: NavController) {
    Scaffold(
        topBar = { TopAppBar(title = { Text("Clip Detail") }) }
    ) { padding ->
        Column(modifier = Modifier.padding(padding).padding(16.dp)) {
            Card(modifier = Modifier.fillMaxWidth().height(200.dp)) {
                // Video Player
            }
            Spacer(modifier = Modifier.height(16.dp))
            Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.errorContainer), modifier = Modifier.fillMaxWidth()) {
                Text("⚠ [Free] This clip has a ClipForge watermark", modifier = Modifier.padding(8.dp))
            }
            Spacer(modifier = Modifier.height(16.dp))
            Text("Clip Title", style = MaterialTheme.typography.titleLarge)
            Text("00:30 → 01:15 (45 sec) • 720p • 10.2MB")
            Spacer(modifier = Modifier.height(24.dp))
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceEvenly) {
                Button(onClick = { /* Download */ }) { Text("Download") }
                OutlinedButton(onClick = { /* Share */ }) { Text("Share") }
            }
            Spacer(modifier = Modifier.height(16.dp))
            TextButton(onClick = { /* Delete */ }, modifier = Modifier.fillMaxWidth()) {
                Text("Delete Clip", color = MaterialTheme.colorScheme.error)
            }
        }
    }
}
""",

    # Feature Screens
    "app/src/main/java/com/clipforge/presentation/screen/features/AIHighlightScreen.kt": """package com.clipforge.presentation.screen.features

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AIHighlightScreen(navController: NavController) {
    var maxHighlights by remember { mutableStateOf(5f) }
    
    Scaffold(
        topBar = { TopAppBar(title = { Text("AI Highlight Detection") }) }
    ) { padding ->
        Column(modifier = Modifier.padding(padding).padding(16.dp)) {
            Text("Max Highlights: ${maxHighlights.toInt()}")
            Slider(value = maxHighlights, onValueChange = { maxHighlights = it }, valueRange = 1f..10f, steps = 8)
            Spacer(modifier = Modifier.height(24.dp))
            Button(onClick = { /* Start Job */ }, modifier = Modifier.fillMaxWidth()) {
                Text("Start Analysis")
            }
        }
    }
}
""",

    "app/src/main/java/com/clipforge/presentation/screen/features/SpeechSearchScreen.kt": """package com.clipforge.presentation.screen.features

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SpeechSearchScreen(navController: NavController) {
    var query by remember { mutableStateOf("") }
    
    Scaffold(
        topBar = { TopAppBar(title = { Text("Speech Search (Premium)") }) }
    ) { padding ->
        Column(modifier = Modifier.padding(padding).padding(16.dp)) {
            OutlinedTextField(
                value = query,
                onValueChange = { query = it },
                label = { Text("Search word or phrase") },
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(modifier = Modifier.height(16.dp))
            Button(onClick = { /* Start Job */ }, modifier = Modifier.fillMaxWidth()) {
                Text("Search & Auto-Clip")
            }
        }
    }
}
""",

    "app/src/main/java/com/clipforge/presentation/screen/features/SceneDetectionScreen.kt": """package com.clipforge.presentation.screen.features

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SceneDetectionScreen(navController: NavController) {
    Scaffold(
        topBar = { TopAppBar(title = { Text("Scene Detection") }) }
    ) { padding ->
        Column(modifier = Modifier.padding(padding).padding(16.dp)) {
            Text("Detect automatic scene cuts in the video.")
            Spacer(modifier = Modifier.height(24.dp))
            Button(onClick = { /* Start Job */ }, modifier = Modifier.fillMaxWidth()) {
                Text("Detect Scenes")
            }
        }
    }
}
""",

    "app/src/main/java/com/clipforge/presentation/screen/features/ObjectTrackingScreen.kt": """package com.clipforge.presentation.screen.features

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ObjectTrackingScreen(navController: NavController) {
    Scaffold(
        topBar = { TopAppBar(title = { Text("Object Tracking (Premium)") }) }
    ) { padding ->
        Column(modifier = Modifier.padding(padding).padding(16.dp)) {
            Text("Select objects to track (e.g. Person, Car, Cat)")
            // Checkboxes placeholder
            Spacer(modifier = Modifier.height(24.dp))
            Button(onClick = { /* Start Job */ }, modifier = Modifier.fillMaxWidth()) {
                Text("Start Tracking")
            }
        }
    }
}
""",

    "app/src/main/java/com/clipforge/presentation/screen/features/FaceTrackingScreen.kt": """package com.clipforge.presentation.screen.features

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FaceTrackingScreen(navController: NavController) {
    Scaffold(
        topBar = { TopAppBar(title = { Text("Face Tracking (Premium)") }) }
    ) { padding ->
        Column(modifier = Modifier.padding(padding).padding(16.dp)) {
            Text("Automatically clip when faces appear.")
            Spacer(modifier = Modifier.height(24.dp))
            Button(onClick = { /* Start Job */ }, modifier = Modifier.fillMaxWidth()) {
                Text("Start Face Tracking")
            }
        }
    }
}
""",

    "app/src/main/java/com/clipforge/presentation/screen/features/GestureTrackingScreen.kt": """package com.clipforge.presentation.screen.features

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun GestureTrackingScreen(navController: NavController) {
    Scaffold(
        topBar = { TopAppBar(title = { Text("Gesture Tracking (Premium)") }) }
    ) { padding ->
        Column(modifier = Modifier.padding(padding).padding(16.dp)) {
            Text("Select gestures to track (Thumbs up, Wave, Pointing, etc)")
            Spacer(modifier = Modifier.height(24.dp))
            Button(onClick = { /* Start Job */ }, modifier = Modifier.fillMaxWidth()) {
                Text("Start Tracking")
            }
        }
    }
}
""",

    "app/src/main/java/com/clipforge/presentation/screen/features/ShortsGeneratorScreen.kt": """package com.clipforge.presentation.screen.features

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ShortsGeneratorScreen(navController: NavController) {
    Scaffold(
        topBar = { TopAppBar(title = { Text("Shorts Generator (Premium)") }) }
    ) { padding ->
        Column(modifier = Modifier.padding(padding).padding(16.dp)) {
            Text("Convert clip to 9:16 vertical video with auto-subtitles and auto-center.")
            Spacer(modifier = Modifier.height(24.dp))
            Button(onClick = { /* Start Job */ }, modifier = Modifier.fillMaxWidth()) {
                Text("Generate Shorts")
            }
        }
    }
}
"""
}

for path, content in files.items():
    full_path = os.path.join("/sdcard/ClipForge/android", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)

print("Android files Part 2 generated successfully.")
