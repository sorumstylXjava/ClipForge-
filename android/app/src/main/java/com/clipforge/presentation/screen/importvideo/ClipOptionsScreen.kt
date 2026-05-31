package com.clipforge.presentation.screen.importvideo

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
