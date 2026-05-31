package com.clipforge.presentation.component

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.List
import androidx.compose.material.icons.filled.PlayArrow
import /* androidx.compose.material.icons.filled.Settings */ androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.navigation.NavController
import com.clipforge.presentation.navigation.Screen

@Composable
fun BottomNavigationBar(navController: NavController, currentRoute: String?) {
    NavigationBar {
        NavigationBarItem(
            icon = { Icon(Icons.Default.Home, contentDescription = "Home") },
            label = { Text("Home") },
            selected = currentRoute == Screen.Home.route,
            onClick = {
                navController.navigate(Screen.Home.route) {
                    popUpTo(Screen.Home.route) { inclusive = true }
                }
            }
        )
        NavigationBarItem(
            icon = { Icon(Icons.Default.PlayArrow, contentDescription = "Clips") },
            label = { Text("Clips") },
            selected = currentRoute == Screen.AIClips.route,
            onClick = { navController.navigate(Screen.AIClips.route) }
        )
        NavigationBarItem(
            icon = { Icon(Icons.Default.List, contentDescription = "Projects") },
            label = { Text("Projects") },
            selected = currentRoute == Screen.Projects.route,
            onClick = { navController.navigate(Screen.Projects.route) }
        )
        NavigationBarItem(
            icon = { Icon(Icons.Default.Settings, contentDescription = "Settings") },
            label = { Text("Settings") },
            selected = currentRoute == Screen.Settings.route,
            onClick = { navController.navigate(Screen.Settings.route) }
        )
    }
}
