# Blender betiği: Teyze karakterini üretir ve glTF (.glb) olarak dışa aktarır.
#
#   blender -b --python FPSBatak/tools/art/build_teyze.py -- FPSBatak/assets/characters/teyze/teyze.glb
#
# Stil: stilize yarı-gerçekçi. Organik formlar metaball (yazma, yüz, hırka, etek,
# kollar) ile kurulur, mesh'e çevrilip seyreltilir (decimate). Renkler vertex
# color'dadır; malzeme yalnızca üç tür: "Cloth" (kumaş, Godot'da örgü dokusu),
# "Smooth" (ten, ahşap, porselen...) ve "Metal" (gözlük). Böylece her parça en
# fazla 2–3 çizim çağrısıdır (mobil bütçe).
#
# Parçalar ve pivotlar (Godot koltuk yereli; -Z masaya bakar):
#   Body  (0,0,0)            — sandalye, kalça/etek, terlik, masadaki çay bardağı
#   Torso (0, 0.58, 0.05)    — hırka, boyun, yaka, düğmeler (nefes pivotu)
#     Head (0, 1.265, -0.015)— yüz, yazma, gözlük (Torso'nun çocuğu)
#   ArmL / ArmR (omuzlar)    — kol + el (kart oynama jesti için)
# Koordinat dönüşümü: Godot (x, y, z) → Blender (x, -z, y); glTF dışa aktarımı geri çevirir.

import math
import sys

import bmesh
import bpy
from mathutils import Matrix, Quaternion, Vector

OUT = sys.argv[sys.argv.index("--") + 1]


def G(x, y, z):
    return Vector((x, -z, y))


# --- Sahneyi temizle ------------------------------------------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# --- Malzemeler -----------------------------------------------------------------------------
def make_mat(name, rough, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    attr = m.node_tree.nodes.new("ShaderNodeVertexColor")
    attr.layer_name = "Col"
    m.node_tree.links.new(attr.outputs["Color"], bsdf.inputs["Base Color"])
    return m


MAT = {"cloth": make_mat("Cloth", 0.95), "smooth": make_mat("Smooth", 0.6), "metal": make_mat("Metal", 0.35, 0.8)}

# Renkler (sRGB)
C = {
    "skin": (0.84, 0.66, 0.56), "cheek": (0.85, 0.63, 0.55), "brow": (0.56, 0.5, 0.47), "line": (0.74, 0.55, 0.46),
    "lip": (0.66, 0.38, 0.36), "eye": (0.07, 0.06, 0.06), "eyewhite": (0.85, 0.83, 0.78),
    "hair": (0.76, 0.74, 0.72), "scarf": (0.58, 0.31, 0.41), "scarf_edge": (0.66, 0.5, 0.48),
    "cardigan": (0.27, 0.4, 0.34), "blouse": (0.7, 0.62, 0.54), "skirt": (0.3, 0.24, 0.27),
    "dark": (0.07, 0.06, 0.06), "wood": (0.3, 0.17, 0.09), "metal": (0.78, 0.65, 0.42),
    "tea": (0.45, 0.2, 0.08), "porcelain": (0.88, 0.85, 0.79), "button": (0.12, 0.1, 0.08),
}


def paint(obj, rgb):
    me = obj.data
    attr = me.color_attributes.get("Col") or me.color_attributes.new("Col", "BYTE_COLOR", "CORNER")
    for d in attr.data:
        d.color_srgb = (*rgb, 1.0)
    me.color_attributes.active_color = attr


def assign(obj, mat_key):
    obj.data.materials.clear()
    obj.data.materials.append(MAT[mat_key])


def finish(obj, mat_key, rgb, smooth=True):
    assign(obj, mat_key)
    paint(obj, rgb)
    if smooth:
        for p in obj.data.polygons:
            p.use_smooth = True
    return obj


# --- Metaball grupları ----------------------------------------------------------------------
def capsule_el(a, b, r, stiff=2.0):
    """İki Godot noktası arasında metaball kapsül (yarı uzunluk = mesafe/2)."""
    va, vb = G(*a), G(*b)
    d = vb - va
    q = Vector((1, 0, 0)).rotation_difference(d.normalized())
    mid = (va + vb) / 2
    return {"type": "CAPSULE", "co": (mid.x, mid.z, -mid.y), "radius": r, "rot": q,
            "half": d.length / 2, "stiff": stiff}


def metaball(name, elements, resolution, threshold=0.6, decimate=None):
    """elements: type, co (Godot), radius, size (Godot eksenlerinde ölçek), rot, neg, stiff, half."""
    mb = bpy.data.metaballs.new(name)
    mb.resolution = resolution
    mb.render_resolution = resolution
    mb.threshold = threshold
    obj = bpy.data.objects.new(name, mb)
    scene.collection.objects.link(obj)
    for e in elements:
        el = mb.elements.new(type=e.get("type", "BALL"))
        el.co = G(*e["co"])
        el.radius = e["radius"]
        el.stiffness = e.get("stiff", 2.0)
        el.use_negative = e.get("neg", False)
        if "half" in e:
            el.size_x = e["half"]
        elif "size" in e:
            sx, sy, sz = e["size"]
            el.size_x, el.size_y, el.size_z = sx, sz, sy   # yarıçapa göre ölçek
        if "rot" in e:
            el.rotation = e["rot"]
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.convert(target="MESH")
    mesh_obj = bpy.context.view_layer.objects.active
    if decimate:
        mod = mesh_obj.modifiers.new("Decimate", "DECIMATE")
        mod.ratio = decimate
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return mesh_obj


def E(co, r, size=None, **kw):
    d = {"type": "ELLIPSOID" if size else "BALL", "co": co, "radius": r}
    if size:
        d["size"] = size
    d.update(kw)
    return d


# --- Küçük ayrıntılar için primitive'ler ----------------------------------------------------
def prim_sphere(co, r, scale=(1, 1, 1), seg=10, rings=6):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, radius=r, location=G(*co))
    o = bpy.context.active_object
    o.scale = (scale[0], scale[2], scale[1])
    return o


def prim_cyl(a, b, r, seg=8, r2=None):
    va, vb = G(*a), G(*b)
    d = vb - va
    bpy.ops.mesh.primitive_cone_add(vertices=seg, radius1=r, radius2=r if r2 is None else r2,
                                    depth=d.length, location=(va + vb) / 2)
    o = bpy.context.active_object
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    return o


def prim_box(co, size):
    bpy.ops.mesh.primitive_cube_add(size=1, location=G(*co))
    o = bpy.context.active_object
    o.scale = (size[0], size[2], size[1])
    return o


def prim_torus(co, major, minor, axis_godot=(0, 0, 1), maj_seg=16, min_seg=4):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=maj_seg,
                                     minor_segments=min_seg, location=G(*co))
    o = bpy.context.active_object
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(G(*axis_godot).normalized())
    return o


def apply_xf(o):
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


def join(name, objs, pivot_godot):
    for o in objs:
        apply_xf(o)
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    o = bpy.context.view_layer.objects.active
    o.name = name
    o.data.name = name
    scene.cursor.location = G(*pivot_godot)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    return o


# ================================ BODY (statik) ================================
# Oturan beden: kalça sandalyede, uyluklar öne, uzun etek dizden yere dökülür.
body_parts = []
skirt = metaball("MB_skirt", [
    E((0, 0.56, 0.06), 0.2, (1.15, 0.7, 1.0)),
    E((0, 0.545, -0.12), 0.2, (1.2, 0.6, 1.0)),
    E((0, 0.5, -0.29), 0.17, (1.3, 0.75, 0.75)),
    E((0, 0.3, -0.33), 0.2, (1.12, 1.15, 0.55)),
    E((0, 0.1, -0.34), 0.21, (1.22, 0.6, 0.6)),
], 0.02, threshold=0.5, decimate=0.55)
body_parts.append(finish(skirt, "cloth", C["skirt"]))
for sx in (-1, 1):
    s = prim_box((sx * 0.095, 0.022, -0.43), (0.085, 0.04, 0.12))
    body_parts.append(finish(s, "smooth", C["dark"], smooth=False))
chair = [prim_box((0, 0.45, 0.05), (0.45, 0.04, 0.42)), prim_box((0, 0.72, 0.255), (0.45, 0.5, 0.035))]
for x, z in ((-0.2, -0.14), (0.2, -0.14), (-0.2, 0.24), (0.2, 0.24)):
    chair.append(prim_box((x, 0.225, z), (0.035, 0.45, 0.035)))
for c in chair:
    body_parts.append(finish(c, "smooth", C["wood"], smooth=False))
glass_low = prim_cyl((0.2, 0.775, -0.43), (0.2, 0.805, -0.43), 0.024, seg=10, r2=0.018)
glass_up = prim_cyl((0.2, 0.805, -0.43), (0.2, 0.845, -0.43), 0.018, seg=10, r2=0.027)
saucer = prim_cyl((0.2, 0.766, -0.43), (0.2, 0.775, -0.43), 0.045, seg=12, r2=0.04)
body_parts += [finish(glass_low, "smooth", C["tea"]), finish(glass_up, "smooth", C["tea"]),
               finish(saucer, "smooth", C["porcelain"])]
body = join("Body", body_parts, (0, 0, 0))

# ================================ TORSO ================================
TORSO_PIV = (0, 0.58, 0.05)
torso_parts = []
cardigan = metaball("MB_cardigan", [
    E((0, 0.66, 0.05), 0.2, (1.05, 0.8, 0.85)),                 # bel
    E((0, 0.85, 0.05), 0.21, (1.05, 1.05, 0.78)),               # göğüs kafesi
    E((0, 0.83, -0.035), 0.14, (1.25, 0.8, 0.8)),               # göğüs
    E((0, 0.98, 0.07), 0.15, (1.25, 0.6, 0.8)),                 # sırt üstü
    E((-0.15, 0.985, 0.05), 0.085), E((0.15, 0.985, 0.05), 0.085),   # omuzlar
], 0.018, threshold=0.5, decimate=0.5)
torso_parts.append(finish(cardigan, "cloth", C["cardigan"]))
neck = prim_cyl((0, 1.0, 0.01), (0, 1.15, -0.03), 0.054, seg=12, r2=0.048)
collar = prim_torus((0, 1.045, 0.0), 0.064, 0.012, axis_godot=(0, 1, 0), maj_seg=18, min_seg=6)
torso_parts += [finish(neck, "smooth", C["skin"]), finish(collar, "smooth", C["blouse"])]
for y, z in ((0.97, -0.115), (0.9, -0.14), (0.83, -0.155)):
    b = prim_sphere((0.03, y, z), 0.008, seg=6, rings=4)
    torso_parts.append(finish(b, "smooth", C["button"]))
torso = join("Torso", torso_parts, TORSO_PIV)

# ================================ HEAD ================================
HEAD = (0, 1.215, -0.04)   # hafif öne eğik, kısa boyunlu yaşlı duruş
def h(x, y, z):
    return (HEAD[0] + x, HEAD[1] + y, HEAD[2] + z)

head_parts = []
skin = metaball("MB_face", [
    E(h(0, 0.005, 0.008), 0.1),
    E(h(0, -0.04, -0.02), 0.09, (1.1, 0.9, 0.95)),                           # geniş, yuvarlak yüz
    E(h(-0.044, -0.036, -0.05), 0.032), E(h(0.044, -0.036, -0.05), 0.032),   # yumuşak yanaklar
    E(h(0, -0.078, -0.045), 0.034),                                          # çene
    E(h(0, -0.014, -0.096), 0.018, (0.85, 1.25, 1.0), stiff=1.5),            # burun
], 0.008, decimate=0.4)
head_parts.append(finish(skin, "smooth", C["skin"]))
scarf = metaball("MB_scarf", [
    E(h(0, 0.03, 0.035), 0.126, (1.03, 1.05, 1.1)),           # başı saran örtü
    E(h(0, -0.06, 0.035), 0.11, (1.05, 0.95, 1.0)),           # yanaklar ve çene yanı
    E(h(0, -0.15, 0.085), 0.1, (1.45, 1.0, 0.6)),             # ensede bağlı uç
    E(h(-0.1, -0.19, 0.04), 0.07, (1.3, 0.5, 1.2)),           # omuzlara dökülen
    E(h(0.1, -0.19, 0.04), 0.07, (1.3, 0.5, 1.2)),
    E(h(0, -0.13, -0.02), 0.075, (1.25, 0.75, 1.1)),          # çene altından boynu saran bağlayış
    E(h(0, -0.025, -0.112), 0.1, (0.76, 0.82, 0.8), neg=True),# yüz açıklığı
], 0.011, threshold=0.55, decimate=0.45)
head_parts.append(finish(scarf, "cloth", C["scarf"]))
for sx in (-1, 1):
    eye = prim_sphere(h(sx * 0.032, 0.008, -0.088), 0.0062, seg=8, rings=4)
    upper = prim_sphere(h(sx * 0.032, 0.014, -0.087), 0.011, scale=(1.3, 0.42, 0.55))      # hafif ağır kapak
    lower = prim_sphere(h(sx * 0.032, 0.001, -0.087), 0.011, scale=(1.25, 0.38, 0.55))     # gülümseyen alt kapak
    cheek = prim_sphere(h(sx * 0.043, -0.03, -0.08), 0.012, scale=(1.15, 0.7, 0.28))
    brow = prim_cyl(h(sx * 0.02, 0.027, -0.092), h(sx * 0.044, 0.024, -0.088), 0.0017, seg=5)
    c1 = prim_cyl(h(sx * 0.05, 0.012, -0.08), h(sx * 0.056, 0.015, -0.075), 0.0012, seg=4)
    c2 = prim_cyl(h(sx * 0.05, 0.003, -0.08), h(sx * 0.056, 0.0, -0.075), 0.0012, seg=4)
    fold_l = prim_cyl(h(sx * 0.018, -0.03, -0.097), h(sx * 0.026, -0.048, -0.093), 0.0014, seg=4)
    lip = prim_cyl(h(0, -0.058, -0.097), h(sx * 0.017, -0.054, -0.093), 0.0024, seg=6)
    head_parts += [finish(eye, "smooth", C["eye"]), finish(upper, "smooth", C["skin"]),
                   finish(lower, "smooth", C["skin"]), finish(cheek, "smooth", C["cheek"]),
                   finish(brow, "smooth", C["brow"]), finish(c1, "smooth", C["line"]),
                   finish(c2, "smooth", C["line"]), finish(fold_l, "smooth", C["line"]),
                   finish(lip, "smooth", C["lip"])]
    ring = prim_torus(h(sx * 0.032, 0.007, -0.1), 0.018, 0.0013, axis_godot=(0, 0, 1))
    temple = prim_cyl(h(sx * 0.05, 0.011, -0.098), h(sx * 0.064, 0.012, -0.075), 0.0012, seg=4)
    head_parts += [finish(ring, "metal", C["metal"]), finish(temple, "metal", C["metal"])]
bridge = prim_cyl(h(-0.014, 0.011, -0.102), h(0.014, 0.011, -0.102), 0.0012, seg=4)
head_parts.append(finish(bridge, "metal", C["metal"]))
head = join("Head", head_parts, HEAD)

# ================================ KOLLAR ================================
ARMS = {
    "L": ((-0.155, 0.99, 0.05), (-0.215, 0.8, -0.06), (-0.118, 0.895, -0.245)),
    "R": ((0.155, 0.99, 0.05), (0.215, 0.8, -0.06), (0.128, 0.9, -0.245)),
}
arm_objs = {}
for side, (sh, el, ha) in ARMS.items():
    sx = 1 if side == "R" else -1
    wrist = tuple(el[i] + (ha[i] - el[i]) * 0.8 for i in range(3))
    sleeve = metaball(f"MB_sleeve{side}", [
        capsule_el((sh[0] - sx * 0.02, sh[1] + 0.01, sh[2]), el, 0.06, 2.5),
        capsule_el(el, wrist, 0.05, 2.5),
        E(wrist, 0.05, (1.0, 1.0, 1.0)),
    ], 0.014, threshold=0.5, decimate=0.5)
    hand = metaball(f"MB_hand{side}", [
        E(ha, 0.036, (0.8, 0.65, 1.15)),
        capsule_el((ha[0] - sx * 0.018, ha[1] + 0.01, ha[2] - 0.018),
                   (ha[0] - sx * 0.03, ha[1] + 0.03, ha[2] - 0.034), 0.011, 1.5),
    ], 0.008, decimate=0.5)
    arm_objs[side] = join(f"Arm{side}", [finish(sleeve, "cloth", C["cardigan"]),
                                          finish(hand, "smooth", C["skin"])], sh)

# --- Hiyerarşi: Head → Torso ----------------------------------------------------------------
bpy.ops.object.select_all(action="DESELECT")
head.select_set(True)
torso.select_set(True)
bpy.context.view_layer.objects.active = torso
bpy.ops.object.parent_set(type="OBJECT", keep_transform=True)

# --- Rapor + dışa aktarım -------------------------------------------------------------------
tris = 0
for o in scene.objects:
    if o.type == "MESH":
        o.data.calc_loop_triangles()
        n = len(o.data.loop_triangles)
        tris += n
        print(f"[teyze] {o.name}: {n} üçgen, malzeme {[m.name for m in o.data.materials]}")
print(f"[teyze] toplam üçgen: {tris}")
bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", use_selection=False,
                          export_vertex_color="ACTIVE", export_all_vertex_colors=False,
                          export_normals=True, export_materials="EXPORT", export_yup=True,
                          export_apply=True)
print("[teyze] yazıldı:", OUT)
