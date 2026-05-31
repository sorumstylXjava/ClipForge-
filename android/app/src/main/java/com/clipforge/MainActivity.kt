package com.clipforge

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import com.clipforge.presentation.navigation.AppNavGraph
import com.clipforge.presentation.theme.ClipForgeTheme
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            ClipForgeTheme {
                AppNavGraph()
            }
        }
    }
}
