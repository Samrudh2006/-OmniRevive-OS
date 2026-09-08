package com.example.razorreviveos.ui.main

import android.Manifest
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.util.Log
import android.view.ViewGroup
import android.webkit.PermissionRequest
import android.webkit.WebChromeClient
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat

@Composable
fun MainScreen(modifier: Modifier = Modifier) {
  val context = LocalContext.current
  var webViewInstance by remember { mutableStateOf<WebView?>(null) }
  var isLoading by remember { mutableStateOf(true) }
  var loadProgress by remember { mutableFloatStateOf(0f) }

  // Microphone Permission Handler for Speech STT & Voice Engine
  val recordAudioLauncher = rememberLauncherForActivityResult(
    contract = ActivityResultContracts.RequestPermission()
  ) { isGranted ->
    if (isGranted) {
      Log.d("RazorRevive", "Record Audio permission granted")
    } else {
      Log.w("RazorRevive", "Record Audio permission denied")
    }
  }

  LaunchedEffect(Unit) {
    if (ContextCompat.checkSelfPermission(context, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
      recordAudioLauncher.launch(Manifest.permission.RECORD_AUDIO)
    }
  }

  // Handle native Android hardware back press
  BackHandler(enabled = webViewInstance?.canGoBack() == true) {
    webViewInstance?.goBack()
  }

  Box(
    modifier = modifier
      .fillMaxSize()
      .background(Color(0xFF071326))
      .statusBarsPadding()
  ) {
    // Hardware-Accelerated Embedded Android WebView (Full-Screen Edge-to-Edge)
    AndroidView(
      factory = { ctx ->
        WebView(ctx).apply {
          layoutParams = ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.MATCH_PARENT
          )

          // High-Performance Web Settings
          settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            databaseEnabled = true
            allowFileAccess = true
            allowContentAccess = true
            useWideViewPort = true
            loadWithOverviewMode = true
            mediaPlaybackRequiresUserGesture = false
            cacheMode = WebSettings.LOAD_DEFAULT
            mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
            userAgentString = "${settings.userAgentString} RazorReviveAndroid/1.0"
          }

          // WebChromeClient with auto-permission granting for WebAudio and Microphone STT
          webChromeClient = object : WebChromeClient() {
            override fun onProgressChanged(view: WebView?, newProgress: Int) {
              loadProgress = newProgress / 100f
              if (newProgress >= 100) {
                isLoading = false
              }
            }

            override fun onPermissionRequest(request: PermissionRequest?) {
              request?.let {
                val resources = it.resources
                val hasAudio = resources.any { res -> res == PermissionRequest.RESOURCE_AUDIO_CAPTURE }
                if (hasAudio) {
                  it.grant(arrayOf(PermissionRequest.RESOURCE_AUDIO_CAPTURE))
                  Log.d("RazorRevive", "Auto-granted WebRTC audio capture for speech engine")
                } else {
                  it.grant(resources)
                }
              }
            }
          }

          // WebViewClient with error and redirection handling
          webViewClient = object : WebViewClient() {
            override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {
              isLoading = true
            }

            override fun onPageFinished(view: WebView?, url: String?) {
              isLoading = false
              // Inject client-side environment hint
              view?.evaluateJavascript(
                """
                (function() {
                  window.IS_ANDROID_NATIVE = true;
                  console.log('RazorRevive-OS Mobile Native Fullscreen Active');
                })();
                """.trimIndent(),
                null
              )
            }

            override fun onReceivedError(view: WebView?, request: WebResourceRequest?, error: WebResourceError?) {
              if (request?.isForMainFrame == true) {
                val errorDesc = error?.description?.toString() ?: "Connection error"
                Log.e("RazorRevive", "Mainframe load error: $errorDesc")
              }
            }
          }

          webViewInstance = this
          // Always load bundled offline asset by default - 100% reliable on any physical phone!
          loadUrl("file:///android_asset/www/index.html")
        }
      },
      modifier = Modifier.fillMaxSize()
    )

    // Subtle loading progress indicator at top edge
    AnimatedVisibility(
      visible = isLoading,
      modifier = Modifier.align(Alignment.TopCenter)
    ) {
      LinearProgressIndicator(
        progress = { loadProgress },
        modifier = Modifier.fillMaxWidth().height(2.5.dp),
        color = Color(0xFF00E5FF),
        trackColor = Color(0xFF0C2340)
      )
    }
  }
}
