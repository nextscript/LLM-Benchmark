# engine.md — Game Engine / Graphics Programming Test Prompts

## Ziel

Diese Datei definiert Benchmark-Testprompts, um zu prüfen, ob ein LLM wirklich gut für Game-Engine-Entwicklung, Rendering, Shader, Vulkan, GLSL, Unity, Unreal, Godot, Performance, Physics und Multiplayer geeignet ist.

Wichtig: Diese Tests sollen nicht nur Syntax prüfen. Sie sollen zeigen, ob das Modell echte Engine-Probleme strukturieren, implementieren, debuggen und optimieren kann.

---

## Empfohlene Bewertung

Jeder Prompt sollte zusätzlich zu normalen Scores einen Engine-Skill-Score bekommen.

### Badge-Stufen

- Grün = `Kann gut` ab 75 Punkten
- Orange = `Kann mittel` ab 45 Punkten
- Rot = `Kann schlecht` unter 45 Punkten

### Empfohlene Kategorien

```text
game_engine_vulkan
game_engine_glsl
game_engine_hlsl
game_engine_opengl
game_engine_directx12
game_engine_webgpu
game_engine_unity
game_engine_unreal
game_engine_godot
game_engine_render_pipeline
game_engine_shader_debugging
game_engine_gpu_performance
game_engine_physics
game_engine_multiplayer
game_engine_asset_pipeline
game_engine_editor_tools
game_engine_gameplay_systems
game_engine_2d
game_engine_3d
```

### Empfohlene Prompt-Struktur in Python

```python
ENGINE_PROMPTS = {
    "engine_vulkan_triangle_swapchain": {
        "name": "Vulkan — Triangle, Swapchain and Synchronization",
        "category": "game_engine_vulkan",
        "engine_skill": "vulkan",
        "engine_skill_label": "Vulkan",
        "difficulty": "hard",
        "text": "...",
        "checks": ["swapchain", "pipeline", "command_buffer", "fence", "semaphore", "validation_layers"],
    }
}
```

---

# 1. Vulkan Tests

## `engine_vulkan_triangle_swapchain` — Triangle, Swapchain and Synchronization

```text
Write a minimal Vulkan renderer in C++ that opens a window and renders a colored triangle. Explain the required Vulkan objects and show the core code structure.

Requirements:
- Create instance, physical device, logical device, surface and swapchain.
- Create image views, render pass, graphics pipeline and framebuffers.
- Record command buffers for drawing a triangle.
- Use semaphores and fences correctly for frames in flight.
- Enable validation layers in debug builds.
- Explain the purpose of each synchronization object.
- Keep the code structured into initialization, draw loop and cleanup sections.
```

Checks:

```python
["instance", "physical_device", "logical_device", "swapchain", "render_pass", "pipeline", "command_buffer", "semaphore", "fence", "validation_layers", "cleanup"]
```

---

## `engine_vulkan_texture_upload` — Texture Upload and Layout Transitions

```text
Write C++ Vulkan code and explanation for uploading a 2D texture from CPU memory to the GPU.

Requirements:
- Use a staging buffer.
- Allocate device-local image memory.
- Copy buffer data into the image.
- Perform correct image layout transitions.
- Create image view and sampler.
- Explain transfer queue usage if available.
- Include common mistakes that cause black textures.
```

Checks:

```python
["staging_buffer", "device_local", "vkCmdCopyBufferToImage", "layout_transition", "image_view", "sampler", "barrier", "black_texture_debugging"]
```

---

## `engine_vulkan_descriptor_sets` — Descriptor Sets and Uniform Buffers

```text
Design and implement the descriptor system for a Vulkan renderer that uses per-frame uniform buffers and combined image samplers.

Requirements:
- Create descriptor set layout.
- Create descriptor pool.
- Allocate descriptor sets for multiple frames in flight.
- Bind uniform buffers and texture samplers.
- Update descriptors safely.
- Explain why descriptor sets are not the same as OpenGL global state.
- Include C++ code snippets.
```

Checks:

```python
["descriptor_set_layout", "descriptor_pool", "allocate_descriptor_sets", "uniform_buffer", "combined_image_sampler", "frames_in_flight", "vkUpdateDescriptorSets"]
```

---

## `engine_vulkan_synchronization_debug` — Synchronization Bug Fix

```text
A Vulkan renderer sometimes flickers, sometimes shows old frames, and validation layers report possible hazards around image layout transitions. Diagnose the likely synchronization problems and provide a corrected synchronization strategy.

Requirements:
- Explain execution dependency vs memory dependency.
- Use pipeline barriers correctly.
- Explain image layout transitions.
- Use acquire/present semaphores correctly.
- Use fences for CPU/GPU frame pacing.
- Mention how to verify the fix with validation layers and RenderDoc.
```

Checks:

```python
["execution_dependency", "memory_dependency", "pipeline_barrier", "image_layout", "acquire_semaphore", "present_semaphore", "fence", "RenderDoc"]
```

---

# 2. GLSL Shader Tests

## `engine_glsl_pbr_fragment_shader` — PBR Fragment Shader

```text
Write a GLSL fragment shader for physically based rendering using metallic-roughness workflow.

Requirements:
- Use albedo, normal, metallic, roughness and ambient occlusion inputs.
- Implement Cook-Torrance BRDF with GGX distribution.
- Include Fresnel-Schlick and geometry term.
- Support at least one directional light.
- Apply gamma correction.
- Explain assumptions and limitations.
```

Checks:

```python
["GLSL", "Cook-Torrance", "GGX", "Fresnel", "metallic", "roughness", "normal", "gamma_correction", "directional_light"]
```

---

## `engine_glsl_normal_mapping` — Tangent Space Normal Mapping

```text
Write a GLSL vertex and fragment shader pair for tangent-space normal mapping.

Requirements:
- Pass position, normal, tangent and UV from vertex shader.
- Build a TBN matrix.
- Sample a normal map.
- Convert sampled normal from texture space to tangent/world space.
- Use the normal in lighting.
- Explain common bugs such as inverted green channel or wrong tangent basis.
```

Checks:

```python
["vertex_shader", "fragment_shader", "TBN", "tangent", "bitangent", "normal_map", "texture_space", "lighting", "inverted_green"]
```

---

## `engine_glsl_shadow_mapping` — Shadow Mapping

```text
Write GLSL shaders and rendering steps for basic shadow mapping.

Requirements:
- Create a depth pass from the light point of view.
- Sample the shadow map in the lighting pass.
- Transform world position into light clip space.
- Apply bias to reduce shadow acne.
- Implement PCF filtering.
- Explain peter-panning and acne tradeoffs.
```

Checks:

```python
["depth_pass", "light_space_matrix", "shadow_map", "bias", "PCF", "shadow_acne", "peter_panning"]
```

---

## `engine_glsl_compute_particles` — Compute Shader Particle Simulation

```text
Write a GLSL compute shader that updates a particle system on the GPU.

Requirements:
- Use shader storage buffer objects.
- Update position and velocity.
- Apply gravity and lifetime.
- Respawn dead particles.
- Use work group size correctly.
- Explain synchronization requirements between compute and render passes.
```

Checks:

```python
["compute_shader", "SSBO", "work_group_size", "position", "velocity", "lifetime", "respawn", "memory_barrier"]
```

---

# 3. HLSL / DirectX Tests

## `engine_hlsl_lighting_shader` — HLSL Lighting Shader

```text
Write an HLSL vertex and pixel shader for textured Blinn-Phong lighting.

Requirements:
- Use constant buffers for matrices and light data.
- Sample a diffuse texture.
- Calculate ambient, diffuse and specular lighting.
- Use normal transformation correctly.
- Explain register bindings.
- Include shader code and a short pipeline explanation.
```

Checks:

```python
["cbuffer", "Texture2D", "SamplerState", "vertex_shader", "pixel_shader", "Blinn-Phong", "register", "normal_transform"]
```

---

## `engine_directx12_resource_barriers` — DirectX 12 Resource Barriers

```text
Explain and implement DirectX 12 resource state transitions for rendering to a texture and then sampling it in a post-processing pass.

Requirements:
- Explain resource states.
- Transition render target to shader resource.
- Use command lists correctly.
- Mention descriptor heaps.
- Show pseudo-code or C++ snippets.
- Explain common mistakes that cause GPU validation errors.
```

Checks:

```python
["D3D12_RESOURCE_STATE_RENDER_TARGET", "D3D12_RESOURCE_STATE_PIXEL_SHADER_RESOURCE", "ResourceBarrier", "command_list", "descriptor_heap", "validation"]
```

---

# 4. OpenGL Tests

## `engine_opengl_deferred_renderer` — Deferred Rendering in OpenGL

```text
Design an OpenGL deferred renderer.

Requirements:
- Create a G-buffer with position, normal, albedo and material data.
- Write geometry pass shaders.
- Write lighting pass logic.
- Explain framebuffer setup.
- Explain how to handle depth, transparency and MSAA limitations.
- Include code snippets for framebuffer and texture attachments.
```

Checks:

```python
["G-buffer", "framebuffer", "texture_attachment", "geometry_pass", "lighting_pass", "depth", "transparency", "MSAA"]
```

---

## `engine_opengl_instancing` — Instanced Rendering

```text
Write an OpenGL example for rendering thousands of identical meshes using instancing.

Requirements:
- Use vertex array objects and vertex buffer objects.
- Upload per-instance transform data.
- Use glVertexAttribDivisor.
- Draw with glDrawElementsInstanced or glDrawArraysInstanced.
- Explain performance benefits and limitations.
```

Checks:

```python
["VAO", "VBO", "instance_buffer", "glVertexAttribDivisor", "glDrawElementsInstanced", "transform", "performance"]
```

---

# 5. WebGPU / WGSL Tests

## `engine_webgpu_triangle_wgsl` — WebGPU Triangle

```text
Write a minimal WebGPU example that renders a triangle using WGSL shaders.

Requirements:
- Request adapter and device.
- Configure canvas context.
- Create render pipeline.
- Write WGSL vertex and fragment shaders.
- Encode commands and submit them.
- Explain how WebGPU differs from WebGL.
```

Checks:

```python
["adapter", "device", "canvas_context", "render_pipeline", "WGSL", "command_encoder", "submit", "WebGL_difference"]
```

---

# 6. Render Pipeline Tests

## `engine_render_forward_plus` — Forward+ Renderer Design

```text
Design a Forward+ renderer for a 3D game engine.

Requirements:
- Explain depth pre-pass.
- Divide the screen into tiles or clusters.
- Cull lights on the GPU.
- Store visible lights per tile or cluster.
- Perform lighting in the main pass.
- Compare Forward+ against classic forward and deferred rendering.
- Include data structures and pass order.
```

Checks:

```python
["depth_prepass", "tiles", "clusters", "light_culling", "compute_shader", "visible_lights", "forward_vs_deferred", "pass_order"]
```

---

## `engine_render_graph` — Render Graph Architecture

```text
Design a render graph system for a custom game engine.

Requirements:
- Represent passes, resources and dependencies.
- Automatically order passes.
- Track texture/resource lifetimes.
- Insert synchronization barriers conceptually.
- Allow transient resources.
- Provide pseudo-code for adding a shadow pass, geometry pass, lighting pass and post-processing pass.
```

Checks:

```python
["render_graph", "passes", "resources", "dependencies", "topological_sort", "resource_lifetime", "barriers", "transient_resources"]
```

---

## `engine_render_hdr_postprocessing` — HDR and Post-Processing Pipeline

```text
Design an HDR rendering and post-processing pipeline.

Requirements:
- Render scene into HDR color buffer.
- Apply bloom extraction and blur.
- Apply tone mapping.
- Apply gamma correction at the correct stage.
- Explain sRGB versus linear color space.
- Include pass order and texture formats.
```

Checks:

```python
["HDR", "bloom", "blur", "tone_mapping", "gamma_correction", "linear_color", "sRGB", "texture_format", "pass_order"]
```

---

# 7. Shader Debugging Tests

## `engine_shader_black_screen_debug` — Black Screen Debugging

```text
A custom engine shows a black screen after adding a new shader pipeline. Give a systematic debugging plan.

Requirements:
- Check shader compilation and linking.
- Check vertex input layout.
- Check uniforms/descriptors.
- Check depth test and culling.
- Check render target format.
- Check camera matrices.
- Explain how to use RenderDoc to inspect the frame.
- Prioritize likely causes.
```

Checks:

```python
["shader_compile", "vertex_layout", "uniforms", "descriptors", "depth_test", "culling", "render_target", "camera_matrix", "RenderDoc"]
```

---

## `engine_shader_wrong_normals_debug` — Wrong Lighting / Normals Debug

```text
A 3D model renders with broken lighting: one side is too dark, normal maps look inverted, and rotating the model changes highlights incorrectly. Diagnose the likely causes and propose fixes.

Requirements:
- Discuss normal matrix.
- Discuss tangent space and TBN correctness.
- Discuss handedness and bitangent sign.
- Discuss sRGB/linear issues for normal maps.
- Discuss imported mesh tangents.
- Provide shader-level and asset-pipeline fixes.
```

Checks:

```python
["normal_matrix", "TBN", "handedness", "bitangent", "normal_map_sRGB", "mesh_tangents", "asset_pipeline", "shader_fix"]
```

---

# 8. GPU Performance Tests

## `engine_gpu_bottleneck_analysis` — GPU Bottleneck Diagnosis

```text
A game runs at 35 FPS on a mid-range GPU. CPU frame time is 8 ms, GPU frame time is 26 ms. Diagnose the bottleneck and propose a prioritized optimization plan.

Requirements:
- Explain CPU frame time vs GPU frame time.
- Identify likely GPU bottleneck.
- Discuss overdraw, shader complexity, shadow quality, post-processing and resolution.
- Explain how to verify with GPU profiler or RenderDoc.
- Provide concrete optimization steps.
```

Checks:

```python
["CPU_frame_time", "GPU_frame_time", "GPU_bottleneck", "overdraw", "shader_complexity", "shadows", "post_processing", "RenderDoc", "optimization_plan"]
```

---

## `engine_draw_call_optimization` — Draw Calls, Batching and Instancing

```text
A scene has 20,000 small objects and the engine is CPU-bound due to draw calls. Propose and implement an optimization strategy.

Requirements:
- Explain draw call overhead.
- Compare static batching, dynamic batching and GPU instancing.
- Use frustum culling.
- Use LODs.
- Discuss material sorting.
- Provide pseudo-code for batching or instancing.
```

Checks:

```python
["draw_call", "CPU_bound", "static_batching", "dynamic_batching", "instancing", "frustum_culling", "LOD", "material_sorting"]
```

---

## `engine_vram_texture_optimization` — VRAM and Texture Optimization

```text
A game exceeds VRAM budget and stutters when entering new areas. Design a texture and asset memory optimization plan.

Requirements:
- Use texture compression.
- Use mipmaps.
- Use streaming.
- Track memory budgets.
- Discuss texture atlases and virtual texturing conceptually.
- Explain how to avoid runtime stalls.
- Provide practical debugging metrics.
```

Checks:

```python
["VRAM", "texture_compression", "mipmaps", "streaming", "memory_budget", "texture_atlas", "virtual_texturing", "runtime_stalls", "metrics"]
```

---

# 9. Unity Tests

## `engine_unity_urp_render_feature` — URP Custom Render Feature

```text
Write a Unity URP custom render feature that applies a simple full-screen post-processing effect.

Requirements:
- Create ScriptableRendererFeature.
- Create ScriptableRenderPass.
- Allocate and use temporary render targets correctly.
- Blit source to destination with a material.
- Expose settings in the inspector.
- Explain where the pass is inserted in the render pipeline.
```

Checks:

```python
["ScriptableRendererFeature", "ScriptableRenderPass", "temporary_render_target", "Blit", "Material", "Inspector", "RenderPassEvent"]
```

---

## `engine_unity_job_system` — Unity Job System and Burst

```text
Convert a slow Unity MonoBehaviour loop that updates 100,000 agents into a Job System implementation.

Requirements:
- Use NativeArray.
- Use IJobParallelFor or equivalent.
- Avoid managed allocations inside jobs.
- Explain Burst compatibility.
- Schedule and complete the job safely.
- Dispose native containers correctly.
```

Checks:

```python
["NativeArray", "IJobParallelFor", "Burst", "Schedule", "Complete", "Dispose", "no_managed_allocation"]
```

---

## `engine_unity_addressables_streaming` — Addressables and Scene Streaming

```text
Design a Unity asset streaming system using Addressables for a large open-world game.

Requirements:
- Load and unload assets asynchronously.
- Manage dependencies.
- Avoid memory leaks.
- Preload nearby areas.
- Handle failed loads.
- Explain how to profile memory usage.
```

Checks:

```python
["Addressables", "async_loading", "unload", "dependencies", "preload", "failed_loads", "memory_profile"]
```

---

# 10. Unreal Engine Tests

## `engine_unreal_cpp_replication_actor` — C++ Actor Replication

```text
Write an Unreal Engine C++ Actor that replicates health and supports a server-authoritative damage function.

Requirements:
- Use replicated properties.
- Implement GetLifetimeReplicatedProps.
- Use server RPC correctly.
- Explain authority checks.
- Notify clients when health changes.
- Include header and source snippets.
```

Checks:

```python
["AActor", "UPROPERTY", "Replicated", "GetLifetimeReplicatedProps", "Server_RPC", "Authority", "OnRep", "health"]
```

---

## `engine_unreal_gas_ability` — Gameplay Ability System Design

```text
Design a simple Unreal Gameplay Ability System setup for a fireball ability.

Requirements:
- Define ability, input activation and cooldown.
- Use gameplay effects for damage and cooldown.
- Explain attributes.
- Explain prediction and server authority.
- Include C++/Blueprint integration notes.
```

Checks:

```python
["GameplayAbility", "GameplayEffect", "Attributes", "Cooldown", "Prediction", "ServerAuthority", "Blueprint", "Input"]
```

---

## `engine_unreal_rdgraph_postprocess` — Render Dependency Graph Concept

```text
Explain how to add a custom post-processing pass in Unreal Engine using Render Dependency Graph concepts.

Requirements:
- Explain RDG pass creation conceptually.
- Explain input and output textures.
- Explain shader parameters.
- Discuss where the pass fits into the renderer.
- Mention debugging and profiling.
```

Checks:

```python
["RDG", "render_pass", "input_texture", "output_texture", "shader_parameters", "post_process", "profiling"]
```

---

# 11. Godot Tests

## `engine_godot_node_signal_system` — Nodes, Scenes and Signals

```text
Create a Godot gameplay system using nodes, scenes and signals for a door that opens when the player collects a key.

Requirements:
- Use separate scenes for Player, Key and Door.
- Use signals for communication.
- Avoid hard-coded global references where possible.
- Include GDScript code.
- Explain the scene tree structure.
```

Checks:

```python
["Node", "Scene", "Signal", "GDScript", "Player", "Key", "Door", "scene_tree", "decoupling"]
```

---

## `engine_godot_shader_water` — Godot Water Shader

```text
Write a Godot shader for stylized water.

Requirements:
- Animate UVs over time.
- Add wave distortion.
- Add fresnel-like edge highlight.
- Support transparency.
- Explain shader parameters for editor tweaking.
```

Checks:

```python
["shader_type", "TIME", "UV", "wave", "fresnel", "transparency", "uniform"]
```

---

## `engine_godot_renderingdevice_compute` — RenderingDevice Compute Concept

```text
Explain how to use Godot RenderingDevice for a compute-style GPU task such as particle simulation.

Requirements:
- Explain buffers.
- Explain shader dispatch.
- Explain synchronization/readback considerations.
- Describe how render data could use compute output.
- Mention common limitations and debugging difficulties.
```

Checks:

```python
["RenderingDevice", "buffer", "compute_shader", "dispatch", "synchronization", "readback", "particles", "debugging"]
```

---

# 12. Physics Tests

## `engine_physics_aabb_collision` — AABB Collision System

```text
Implement a simple 2D AABB collision system in code.

Requirements:
- Define AABB data structure.
- Detect overlap.
- Resolve collision with minimum translation vector.
- Separate dynamic and static objects.
- Explain tunneling and how continuous collision detection helps.
- Include test cases.
```

Checks:

```python
["AABB", "overlap", "MTV", "static", "dynamic", "tunneling", "CCD", "tests"]
```

---

## `engine_physics_spatial_partitioning` — Broadphase Spatial Partitioning

```text
Design a broadphase collision system for thousands of objects.

Requirements:
- Compare grid, quadtree, octree and BVH.
- Pick one approach for a 2D top-down game.
- Provide insertion/query pseudo-code.
- Explain performance tradeoffs.
- Explain when the structure should be rebuilt or updated incrementally.
```

Checks:

```python
["broadphase", "grid", "quadtree", "octree", "BVH", "query", "performance", "incremental_update"]
```

---

# 13. Multiplayer Tests

## `engine_multiplayer_prediction_reconciliation` — Client Prediction and Server Reconciliation

```text
Design a multiplayer movement system with client-side prediction and server reconciliation.

Requirements:
- Explain input sequence numbers.
- Simulate movement locally.
- Send inputs to the server.
- Receive authoritative state.
- Re-apply unacknowledged inputs.
- Smooth corrections.
- Explain common desync causes.
```

Checks:

```python
["client_prediction", "server_reconciliation", "input_sequence", "authoritative_server", "replay_inputs", "smoothing", "desync"]
```

---

## `engine_multiplayer_snapshot_interpolation` — Snapshot Interpolation

```text
Explain and implement snapshot interpolation for remote players in an online game.

Requirements:
- Buffer server snapshots.
- Interpolate between snapshots with a delay.
- Handle packet loss and jitter.
- Explain tick rate vs render frame rate.
- Provide pseudo-code.
```

Checks:

```python
["snapshot", "interpolation", "buffer", "packet_loss", "jitter", "tick_rate", "render_frame_rate", "pseudo_code"]
```

---

# 14. Asset Pipeline Tests

## `engine_asset_gltf_importer` — glTF Asset Import Pipeline

```text
Design a glTF import pipeline for a custom engine.

Requirements:
- Load meshes, materials, textures, skeletons and animations.
- Generate or validate tangents.
- Convert materials to the engine format.
- Create runtime-ready binary cache files.
- Handle missing textures and invalid data.
- Explain how hot reload should work.
```

Checks:

```python
["glTF", "mesh", "material", "texture", "skeleton", "animation", "tangent", "binary_cache", "hot_reload", "invalid_data"]
```

---

## `engine_asset_texture_compression` — Texture Compression Pipeline

```text
Design a texture compression pipeline for PC and mobile builds.

Requirements:
- Choose formats for albedo, normal maps, masks and HDR textures.
- Generate mipmaps.
- Handle sRGB and linear textures correctly.
- Explain platform-specific compression choices.
- Include validation rules.
```

Checks:

```python
["texture_compression", "albedo", "normal_map", "mipmaps", "sRGB", "linear", "platform", "validation"]
```

---

# 15. Editor Tool Tests

## `engine_editor_level_validation_tool` — Level Validation Tool

```text
Design an editor tool that scans a game level for common problems before shipping.

Requirements:
- Detect missing materials, missing collision, broken references and oversized textures.
- Report severity levels.
- Provide clickable links to objects if the engine supports it.
- Allow automatic fixes for safe cases.
- Export a JSON report.
```

Checks:

```python
["editor_tool", "missing_material", "missing_collision", "broken_reference", "oversized_texture", "severity", "auto_fix", "JSON_report"]
```

---

## `engine_editor_debug_overlay` — Runtime Debug Overlay

```text
Design and implement a runtime debug overlay for a game engine.

Requirements:
- Show FPS, frame time, CPU time, GPU time and memory usage.
- Show draw calls and triangle count if available.
- Toggle visibility at runtime.
- Keep overhead low.
- Explain how data is collected.
```

Checks:

```python
["FPS", "frame_time", "CPU_time", "GPU_time", "memory", "draw_calls", "triangles", "toggle", "low_overhead"]
```

---

# 16. Gameplay System Tests

## `engine_gameplay_inventory_system` — Inventory System

```text
Design and implement an inventory system for an RPG.

Requirements:
- Support stackable and non-stackable items.
- Support item metadata.
- Support add, remove, move and split stack operations.
- Prevent invalid states.
- Serialize and deserialize inventory data.
- Include edge cases.
```

Checks:

```python
["inventory", "stackable", "metadata", "add", "remove", "split_stack", "serialization", "edge_cases"]
```

---

## `engine_gameplay_save_load_system` — Save/Load System

```text
Design a robust save/load system for a game.

Requirements:
- Save player stats, inventory, quest state and world state.
- Use versioned save data.
- Handle missing or old fields.
- Avoid corrupted saves by writing atomically.
- Discuss encryption/compression optionally.
- Include data schema example.
```

Checks:

```python
["save_load", "versioning", "inventory", "quest_state", "world_state", "migration", "atomic_write", "schema"]
```

---

# 17. 2D Engine Tests

## `engine_2d_tilemap_renderer` — Tilemap Renderer

```text
Design a performant 2D tilemap renderer.

Requirements:
- Use chunks.
- Batch tiles by texture/material.
- Support camera culling.
- Support animated tiles.
- Support tile collision data.
- Explain how to update only dirty chunks.
```

Checks:

```python
["tilemap", "chunks", "batching", "camera_culling", "animated_tiles", "collision", "dirty_chunks"]
```

---

## `engine_2d_pixel_perfect_camera` — Pixel-Perfect Camera

```text
Implement a pixel-perfect camera system for a 2D game.

Requirements:
- Preserve integer scaling.
- Avoid subpixel jitter.
- Support different screen resolutions.
- Explain render texture approach.
- Handle UI scaling separately.
```

Checks:

```python
["pixel_perfect", "integer_scaling", "subpixel_jitter", "resolution", "render_texture", "UI_scaling"]
```

---

# 18. 3D Engine Tests

## `engine_3d_skeletal_animation` — Skeletal Animation System

```text
Design a skeletal animation system for a 3D engine.

Requirements:
- Load skeleton hierarchy.
- Store inverse bind pose matrices.
- Interpolate keyframes.
- Blend two animations.
- Upload bone matrices to the GPU.
- Explain CPU skinning vs GPU skinning.
```

Checks:

```python
["skeleton", "inverse_bind_pose", "keyframe_interpolation", "animation_blending", "bone_matrices", "GPU_skinning", "CPU_skinning"]
```

---

## `engine_3d_lod_occlusion_streaming` — LOD, Occlusion and Scene Streaming

```text
Design a large 3D world rendering system.

Requirements:
- Use LODs.
- Use frustum culling.
- Use occlusion culling.
- Stream world chunks asynchronously.
- Manage memory budget.
- Avoid visible popping.
- Explain debugging metrics.
```

Checks:

```python
["LOD", "frustum_culling", "occlusion_culling", "streaming", "chunks", "memory_budget", "popping", "metrics"]
```

---

# 19. Schnelltest-Set

Wenn nur wenige Tests laufen sollen, nutze diese 10 Prompts:

```text
engine_vulkan_triangle_swapchain
engine_vulkan_texture_upload
engine_glsl_pbr_fragment_shader
engine_glsl_compute_particles
engine_opengl_deferred_renderer
engine_unity_urp_render_feature
engine_unreal_cpp_replication_actor
engine_godot_node_signal_system
engine_gpu_bottleneck_analysis
engine_draw_call_optimization
```

Diese 10 decken Low-Level Graphics, Shader, Engines, Debugging und Performance ab.

---

# 20. Empfohlene Engine-Badges

```text
Vulkan: Kann gut / Kann mittel / Kann schlecht
GLSL: Kann gut / Kann mittel / Kann schlecht
HLSL: Kann gut / Kann mittel / Kann schlecht
OpenGL: Kann gut / Kann mittel / Kann schlecht
DirectX 12: Kann gut / Kann mittel / Kann schlecht
WebGPU: Kann gut / Kann mittel / Kann schlecht
Unity: Kann gut / Kann mittel / Kann schlecht
Unreal: Kann gut / Kann mittel / Kann schlecht
Godot: Kann gut / Kann mittel / Kann schlecht
Rendering: Kann gut / Kann mittel / Kann schlecht
Shader: Kann gut / Kann mittel / Kann schlecht
Physics: Kann gut / Kann mittel / Kann schlecht
Multiplayer: Kann gut / Kann mittel / Kann schlecht
Optimization: Kann gut / Kann mittel / Kann schlecht
Asset Pipeline: Kann gut / Kann mittel / Kann schlecht
Editor Tools: Kann gut / Kann mittel / Kann schlecht
2D Engine: Kann gut / Kann mittel / Kann schlecht
3D Engine: Kann gut / Kann mittel / Kann schlecht
```

---

# 21. Akzeptanzkriterien für Codex

Codex soll die Prompts so übernehmen, dass:

- Jeder Prompt einen stabilen Key hat.
- Jeder Prompt eine Kategorie hat.
- Jeder Prompt ein `engine_skill` und `engine_skill_label` hat.
- Jeder Prompt eigene `checks` besitzt.
- Die Prompts in der WebGUI gruppiert angezeigt werden.
- Ergebnisse pro Engine-Skill gespeichert werden.
- Ranking und Results Engine-Badges anzeigen können.
- Alte Ergebnisse ohne Engine-Skill nicht crashen.
- Schnelltest-Set optional auswählbar ist.

---

# 22. Optionaler späterer Ausbau

Für echte Verifikation später ergänzen:

- Shader-Kompilierung mit `glslangValidator`
- SPIR-V Validierung mit `spirv-val`
- HLSL-Kompilierung mit `dxc`
- C++ Build-Test mit `cmake` und `ninja`
- Vulkan Smoke-Test mit Headless-Renderer
- RenderDoc Capture Check manuell oder halbautomatisch
- Unity Batchmode Tests
- Unreal Automation Tests
- Godot Headless Tests
- Golden Image Tests für Render-Ausgaben

Aktuell reicht für den ersten Umbau eine heuristische Bewertung über Antwortqualität, Syntax-Marker, Engine-Begriffe, Architektur-Verständnis und Required Checks.
