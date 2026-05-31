package com.clipforge.presentation.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
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
            composable(
                route = Screen.VideoMetadataPreview.route,
                arguments = listOf(navArgument("videoId") { type = NavType.StringType })
            ) { VideoMetadataPreviewScreen(navController) }
            composable(
                route = Screen.ClipOptions.route,
                arguments = listOf(navArgument("videoId") { type = NavType.StringType })
            ) { ClipOptionsScreen(navController) }
            composable(
                route = Screen.ManualClip.route,
                arguments = listOf(navArgument("videoId") { type = NavType.StringType })
            ) { ManualClipScreen(navController) }
            composable(
                route = Screen.ClipDetail.route,
                arguments = listOf(navArgument("clipId") { type = NavType.StringType })
            ) { ClipDetailScreen(navController) }
            
            // AI Features
            composable(
                route = Screen.AIHighlight.route,
                arguments = listOf(navArgument("videoId") { type = NavType.StringType })
            ) { AIHighlightScreen(navController) }
            composable(
                route = Screen.SpeechSearch.route,
                arguments = listOf(navArgument("videoId") { type = NavType.StringType })
            ) { SpeechSearchScreen(navController) }
            composable(
                route = Screen.SceneDetection.route,
                arguments = listOf(navArgument("videoId") { type = NavType.StringType })
            ) { SceneDetectionScreen(navController) }
            composable(
                route = Screen.ObjectTracking.route,
                arguments = listOf(navArgument("videoId") { type = NavType.StringType })
            ) { ObjectTrackingScreen(navController) }
            composable(
                route = Screen.FaceTracking.route,
                arguments = listOf(navArgument("videoId") { type = NavType.StringType })
            ) { FaceTrackingScreen(navController) }
            composable(
                route = Screen.GestureTracking.route,
                arguments = listOf(navArgument("videoId") { type = NavType.StringType })
            ) { GestureTrackingScreen(navController) }
            composable(
                route = Screen.ShortsGenerator.route,
                arguments = listOf(navArgument("clipId") { type = NavType.StringType })
            ) { ShortsGeneratorScreen(navController) }
        }
    }
}
