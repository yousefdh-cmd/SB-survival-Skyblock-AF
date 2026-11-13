import os

FILES = {}
J = "src/main/java/com/example/skyblockmod/"
R = "src/main/resources/"

# ═══════════════ ملفات الإعداد ═══════════════

FILES["settings.gradle"] = r'''
pluginManagement {
    repositories {
        gradlePluginPortal()
        maven { url = 'https://maven.neoforged.net/releases' }
    }
}

plugins {
    id 'org.gradle.toolchains.foojay-resolver-convention' version '0.8.0'
}

rootProject.name = 'skyblockmod'
'''

FILES["gradle.properties"] = r'''
org.gradle.jvmargs=-Xmx2G
org.gradle.daemon=true
org.gradle.parallel=true
org.gradle.caching=true

mod_id=skyblockmod
mod_version=0.1.0
mod_group_id=com.example.skyblockmod
neo_version=21.1.77
'''

FILES["build.gradle"] = r'''
plugins {
    id 'java-library'
    id 'idea'
    id 'net.neoforged.moddev' version '1.0.21'
}

version = mod_version
group = mod_group_id

base {
    archivesName = mod_id
}

java.toolchain.languageVersion = JavaLanguageVersion.of(21)

neoForge {
    version = project.neo_version

    runs {
        client {
            client()
        }
        server {
            server()
            programArgument '--nogui'
        }
    }

    mods {
        "${mod_id}" {
            sourceSet sourceSets.main
        }
    }
}

tasks.withType(JavaCompile).configureEach {
    options.encoding = 'UTF-8'
}
'''

FILES[".gitignore"] = r'''
.gradle/
build/
run/
.idea/
*.iml
out/
.vscode/
.classpath
.project
.settings/
eclipse/
'''

FILES["README.md"] = r'''
# SkyBlock Mod (NeoForge 1.21.1)

SkyBlock-style stats, mana and special items. No XP, no grinding: everything is available from the start.

- Creative tab: **SkyBlock**
- Command: `/sb` shows your stats
- Give items: `/give @s skyblockmod:aspect_of_the_end`
'''

FILES[".github/workflows/build.yml"] = r'''
name: Build Mod

on:
  push:
  pull_request:
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: 21

      - uses: gradle/actions/setup-gradle@v4
        with:
          gradle-version: 8.10.2

      - name: Build
        run: gradle build

      - name: Upload jar
        uses: actions/upload-artifact@v4
        with:
          name: skyblockmod
          path: build/libs/*.jar
'''

# ═══════════════ الموارد ═══════════════

FILES[R + "META-INF/neoforge.mods.toml"] = r'''
modLoader="javafml"
loaderVersion="[1,)"
license="MIT"

[[mods]]
modId="skyblockmod"
version="0.1.0"
displayName="SkyBlock Mod"
description="SkyBlock-style stats, mana and special items. No grinding required."

[[dependencies.skyblockmod]]
modId="neoforge"
type="required"
versionRange="[21.1.0,)"
ordering="NONE"
side="BOTH"

[[dependencies.skyblockmod]]
modId="minecraft"
type="required"
versionRange="[1.21.1]"
ordering="NONE"
side="BOTH"
'''

FILES[R + "assets/skyblockmod/lang/en_us.json"] = r'''
{
  "item.skyblockmod.aspect_of_the_end": "Aspect of the End",
  "item.skyblockmod.rogue_sword": "Rogue Sword",
  "itemGroup.skyblockmod": "SkyBlock"
}
'''

FILES[R + "assets/skyblockmod/lang/ar_sa.json"] = r'''
{
  "item.skyblockmod.aspect_of_the_end": "جوهر النهاية",
  "item.skyblockmod.rogue_sword": "سيف المحتال",
  "itemGroup.skyblockmod": "سكاي بلوك"
}
'''

FILES[R + "assets/skyblockmod/models/item/aspect_of_the_end.json"] = r'''
{
  "parent": "minecraft:item/handheld",
  "textures": {
    "layer0": "minecraft:item/diamond_sword"
  }
}
'''

FILES[R + "assets/skyblockmod/models/item/rogue_sword.json"] = r'''
{
  "parent": "minecraft:item/handheld",
  "textures": {
    "layer0": "minecraft:item/golden_sword"
  }
}
'''

# ═══════════════ الكود الرئيسي ═══════════════

FILES[J + "SkyblockMod.java"] = r'''
package com.example.skyblockmod;

import com.example.skyblockmod.data.ModAttachments;
import com.example.skyblockmod.item.ModCreativeTabs;
import com.example.skyblockmod.item.ModItems;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;

@Mod(SkyblockMod.MODID)
public class SkyblockMod {
    public static final String MODID = "skyblockmod";

    public SkyblockMod(IEventBus modBus) {
        ModItems.ITEMS.register(modBus);
        ModCreativeTabs.TABS.register(modBus);
        ModAttachments.ATTACHMENTS.register(modBus);
    }
}
'''

# ═══════════════ data ═══════════════

FILES[J + "data/SkyData.java"] = r'''
package com.example.skyblockmod.data;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;

/** بيانات اللاعب المحفوظة: Mana فقط */
public class SkyData {
    public static final Codec<SkyData> CODEC = RecordCodecBuilder.create(i -> i.group(
            Codec.DOUBLE.optionalFieldOf("mana", 100.0).forGetter(d -> d.mana)
    ).apply(i, SkyData::new));

    public double mana = 100;

    public SkyData() {}

    private SkyData(double mana) {
        this.mana = mana;
    }
}
'''

FILES[J + "data/ModAttachments.java"] = r'''
package com.example.skyblockmod.data;

import com.example.skyblockmod.SkyblockMod;
import net.neoforged.neoforge.attachment.AttachmentType;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.neoforged.neoforge.registries.NeoForgeRegistries;

import java.util.function.Supplier;

public class ModAttachments {
    public static final DeferredRegister<AttachmentType<?>> ATTACHMENTS =
            DeferredRegister.create(NeoForgeRegistries.ATTACHMENT_TYPES, SkyblockMod.MODID);

    public static final Supplier<AttachmentType<SkyData>> SKY_DATA = ATTACHMENTS.register(
            "sky_data",
            () -> AttachmentType.builder(SkyData::new)
                    .serialize(SkyData.CODEC)
                    .copyOnDeath()
                    .build());
}
'''

# ═══════════════ stats ═══════════════

FILES[J + "stats/SkyStats.java"] = r'''
package com.example.skyblockmod.stats;

public record SkyStats(int damage, int strength, int critChance, int critDamage,
                       int defense, int health, int intelligence) {

    public static final SkyStats ZERO = new SkyStats(0, 0, 0, 0, 0, 0, 0);

    public SkyStats plus(SkyStats o) {
        return new SkyStats(
                damage + o.damage, strength + o.strength,
                critChance + o.critChance, critDamage + o.critDamage,
                defense + o.defense, health + o.health,
                intelligence + o.intelligence);
    }

    public boolean isEmpty() {
        return equals(ZERO);
    }
}
'''

FILES[J + "stats/VanillaStats.java"] = r'''
package com.example.skyblockmod.stats;

import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;

import java.util.HashMap;
import java.util.Map;

/** إحصائيات الأدوات والدروع الأصلية. القيم تقديرية، عدّلها حسب الويكي. */
public class VanillaStats {
    private static final Map<Item, SkyStats> MAP = new HashMap<>();

    public static SkyStats get(Item item) {
        return MAP.getOrDefault(item, SkyStats.ZERO);
    }

    private static void dmg(Item item, int damage) {
        MAP.put(item, new SkyStats(damage, 0, 0, 0, 0, 0, 0));
    }

    private static void def(Item item, int defense) {
        MAP.put(item, new SkyStats(0, 0, 0, 0, defense, 0, 0));
    }

    static {
        // ── السيوف ──
        dmg(Items.WOODEN_SWORD, 20);
        dmg(Items.STONE_SWORD, 25);
        dmg(Items.GOLDEN_SWORD, 20);
        dmg(Items.IRON_SWORD, 30);
        dmg(Items.DIAMOND_SWORD, 35);
        dmg(Items.NETHERITE_SWORD, 40);

        // ── الفؤوس ──
        dmg(Items.WOODEN_AXE, 10);
        dmg(Items.STONE_AXE, 15);
        dmg(Items.GOLDEN_AXE, 10);
        dmg(Items.IRON_AXE, 20);
        dmg(Items.DIAMOND_AXE, 25);
        dmg(Items.NETHERITE_AXE, 30);

        // ── المعاول ──
        dmg(Items.WOODEN_PICKAXE, 5);
        dmg(Items.STONE_PICKAXE, 8);
        dmg(Items.GOLDEN_PICKAXE, 5);
        dmg(Items.IRON_PICKAXE, 10);
        dmg(Items.DIAMOND_PICKAXE, 15);
        dmg(Items.NETHERITE_PICKAXE, 20);

        // ── المجارف ──
        dmg(Items.WOODEN_SHOVEL, 3);
        dmg(Items.STONE_SHOVEL, 5);
        dmg(Items.GOLDEN_SHOVEL, 3);
        dmg(Items.IRON_SHOVEL, 8);
        dmg(Items.DIAMOND_SHOVEL, 10);
        dmg(Items.NETHERITE_SHOVEL, 12);

        // ── الدروع (نقاط الدرع الأصلية × 5) ──
        def(Items.LEATHER_HELMET, 5);     def(Items.LEATHER_CHESTPLATE, 15);
        def(Items.LEATHER_LEGGINGS, 10);  def(Items.LEATHER_BOOTS, 5);

        def(Items.CHAINMAIL_HELMET, 10);  def(Items.CHAINMAIL_CHESTPLATE, 25);
        def(Items.CHAINMAIL_LEGGINGS, 20); def(Items.CHAINMAIL_BOOTS, 5);

        def(Items.IRON_HELMET, 10);       def(Items.IRON_CHESTPLATE, 30);
        def(Items.IRON_LEGGINGS, 25);     def(Items.IRON_BOOTS, 10);

        def(Items.GOLDEN_HELMET, 10);     def(Items.GOLDEN_CHESTPLATE, 25);
        def(Items.GOLDEN_LEGGINGS, 15);   def(Items.GOLDEN_BOOTS, 5);

        def(Items.DIAMOND_HELMET, 15);    def(Items.DIAMOND_CHESTPLATE, 40);
        def(Items.DIAMOND_LEGGINGS, 30);  def(Items.DIAMOND_BOOTS, 15);

        def(Items.NETHERITE_HELMET, 20);  def(Items.NETHERITE_CHESTPLATE, 45);
        def(Items.NETHERITE_LEGGINGS, 35); def(Items.NETHERITE_BOOTS, 20);
    }
}
'''

FILES[J + "stats/StatCalculator.java"] = r'''
package com.example.skyblockmod.stats;

import com.example.skyblockmod.item.SkyItem;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;

public class StatCalculator {
    // الإحصائيات الأساسية: Crit Chance 30% / Crit Damage 50% / Health 100 / Intelligence 100
    public static final SkyStats BASE = new SkyStats(0, 0, 30, 50, 0, 100, 100);

    private static final EquipmentSlot[] SLOTS = {
            EquipmentSlot.MAINHAND, EquipmentSlot.HEAD, EquipmentSlot.CHEST,
            EquipmentSlot.LEGS, EquipmentSlot.FEET
    };

    /** إحصائيات عنصر واحد: عنصر المود أو عنصر أصلي */
    public static SkyStats statsOf(ItemStack stack) {
        if (stack.getItem() instanceof SkyItem si) return si.getStats();
        return VanillaStats.get(stack.getItem());
    }

    public static SkyStats compute(Player player) {
        SkyStats total = BASE;
        for (EquipmentSlot slot : SLOTS) {
            total = total.plus(statsOf(player.getItemBySlot(slot)));
        }
        return total;
    }

    public static int maxMana(SkyStats stats) {
        return Math.max(1, stats.intelligence());
    }
}
'''

# ═══════════════ item ═══════════════

FILES[J + "item/SkyRarity.java"] = r'''
package com.example.skyblockmod.item;

import net.minecraft.ChatFormatting;

public enum SkyRarity {
    COMMON("COMMON", ChatFormatting.WHITE),
    UNCOMMON("UNCOMMON", ChatFormatting.GREEN),
    RARE("RARE", ChatFormatting.BLUE),
    EPIC("EPIC", ChatFormatting.DARK_PURPLE),
    LEGENDARY("LEGENDARY", ChatFormatting.GOLD),
    MYTHIC("MYTHIC", ChatFormatting.LIGHT_PURPLE);

    public final String label;
    public final ChatFormatting color;

    SkyRarity(String label, ChatFormatting color) {
        this.label = label;
        this.color = color;
    }
}
'''

FILES[J + "item/SkyAbility.java"] = r'''
package com.example.skyblockmod.item;

import net.minecraft.server.level.ServerPlayer;

/** قدرة خاصة بعنصر: اسم + وصف + تكلفة Mana + ما يحدث عند الضغط الأيمن */
public record SkyAbility(String name, String description, int manaCost, Action action) {

    @FunctionalInterface
    public interface Action {
        void run(ServerPlayer player);
    }
}
'''

FILES[J + "item/Abilities.java"] = r'''
package com.example.skyblockmod.item;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/** مكتبة قدرات جاهزة لإعادة الاستخدام */
public class Abilities {

    public static void teleport(ServerPlayer sp, int range, int speedTicks) {
        Level level = sp.level();
        Vec3 look = sp.getLookAngle();
        Vec3 start = sp.position();
        Vec3 best = start;

        for (int i = 1; i <= range; i++) {
            Vec3 p = start.add(look.scale(i));
            BlockPos feet = BlockPos.containing(p);
            BlockPos head = feet.above();
            boolean free = level.getBlockState(feet).getCollisionShape(level, feet).isEmpty()
                    && level.getBlockState(head).getCollisionShape(level, head).isEmpty();
            if (!free) break;
            best = p;
        }

        sp.teleportTo(best.x, best.y, best.z);
        sp.fallDistance = 0;
        level.playSound(null, sp.blockPosition(), SoundEvents.ENDERMAN_TELEPORT,
                SoundSource.PLAYERS, 1f, 1f);
        if (speedTicks > 0) {
            sp.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, speedTicks, 1));
        }
    }

    public static void speedBoost(ServerPlayer sp, int ticks, int amplifier) {
        sp.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, ticks, amplifier));
    }
}
'''

FILES[J + "item/SkyItem.java"] = r'''
package com.example.skyblockmod.item;

import com.example.skyblockmod.data.ModAttachments;
import com.example.skyblockmod.data.SkyData;
import com.example.skyblockmod.event.SkyEvents;
import com.example.skyblockmod.stats.SkyStats;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;

import java.util.List;

/** عنصر Skyblock عام: إحصائيات + ندرة + قدرة اختيارية. لا توجد أي شروط لاستخدامه. */
public class SkyItem extends Item {
    private final SkyStats stats;
    private final SkyRarity rarity;
    private final SkyAbility ability; // يمكن أن تكون null

    public SkyItem(Properties props, SkyStats stats, SkyRarity rarity, SkyAbility ability) {
        super(props);
        this.stats = stats;
        this.rarity = rarity;
        this.ability = ability;
    }

    public SkyStats getStats() { return stats; }
    public SkyRarity getRarity() { return rarity; }

    @Override
    public Component getName(ItemStack stack) {
        return super.getName(stack).copy().withStyle(rarity.color);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (ability == null) return InteractionResultHolder.pass(stack);

        if (!level.isClientSide && player instanceof ServerPlayer sp) {
            SkyData data = sp.getData(ModAttachments.SKY_DATA);
            if (data.mana < ability.manaCost()) {
                sp.displayClientMessage(Component.literal("Not enough mana!")
                        .withStyle(ChatFormatting.RED), true);
                return InteractionResultHolder.fail(stack);
            }
            data.mana -= ability.manaCost();
            ability.action().run(sp);
            sp.displayClientMessage(Component.literal("Used " + ability.name() + "! (-"
                    + ability.manaCost() + " Mana)").withStyle(ChatFormatting.AQUA), true);
            SkyEvents.sync(sp);
        }
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
    }

    @Override
    public void appendHoverText(ItemStack stack, Item.TooltipContext ctx,
                                List<Component> tooltip, TooltipFlag flag) {
        line(tooltip, "Damage", stats.damage(), ChatFormatting.RED, "");
        line(tooltip, "Strength", stats.strength(), ChatFormatting.RED, "");
        line(tooltip, "Crit Chance", stats.critChance(), ChatFormatting.BLUE, "%");
        line(tooltip, "Crit Damage", stats.critDamage(), ChatFormatting.BLUE, "%");
        line(tooltip, "Health", stats.health(), ChatFormatting.RED, "");
        line(tooltip, "Defense", stats.defense(), ChatFormatting.GREEN, "");
        line(tooltip, "Intelligence", stats.intelligence(), ChatFormatting.AQUA, "");

        if (ability != null) {
            tooltip.add(Component.empty());
            tooltip.add(Component.literal("Ability: " + ability.name() + " ")
                    .withStyle(ChatFormatting.GOLD)
                    .append(Component.literal("RIGHT CLICK")
                            .withStyle(ChatFormatting.YELLOW, ChatFormatting.BOLD)));
            tooltip.add(Component.literal(ability.description()).withStyle(ChatFormatting.GRAY));
            tooltip.add(Component.literal("Mana Cost: ").withStyle(ChatFormatting.DARK_GRAY)
                    .append(Component.literal(String.valueOf(ability.manaCost()))
                            .withStyle(ChatFormatting.DARK_AQUA)));
        }

        tooltip.add(Component.empty());
        tooltip.add(Component.literal(rarity.label).withStyle(rarity.color, ChatFormatting.BOLD));
    }

    private static void line(List<Component> tooltip, String name, int value,
                             ChatFormatting color, String suffix) {
        if (value == 0) return;
        tooltip.add(Component.literal(name + ": ").withStyle(ChatFormatting.GRAY)
                .append(Component.literal("+" + value + suffix).withStyle(color)));
    }
}
'''

FILES[J + "item/ModItems.java"] = r'''
package com.example.skyblockmod.item;

import com.example.skyblockmod.SkyblockMod;
import com.example.skyblockmod.stats.SkyStats;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.Tiers;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

public class ModItems {
    public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(SkyblockMod.MODID);

    private static Item.Properties sword() {
        return new Item.Properties().stacksTo(1)
                .attributes(SwordItem.createAttributes(Tiers.DIAMOND, 3, -2.4f));
    }

    // SkyStats(damage, strength, critChance, critDamage, defense, health, intelligence)

    public static final DeferredItem<SkyItem> ASPECT_OF_THE_END = ITEMS.register("aspect_of_the_end",
            () -> new SkyItem(sword(),
                    new SkyStats(100, 100, 0, 0, 0, 0, 0),
                    SkyRarity.RARE,
                    new SkyAbility("Instant Transmission",
                            "Teleport 8 blocks ahead of you and gain +50 speed for 3 seconds.",
                            50,
                            sp -> Abilities.teleport(sp, 8, 60))));

    public static final DeferredItem<SkyItem> ROGUE_SWORD = ITEMS.register("rogue_sword",
            () -> new SkyItem(sword(),
                    new SkyStats(20, 0, 0, 0, 0, 0, 0),
                    SkyRarity.COMMON,
                    new SkyAbility("Speed Boost",
                            "Grants +100 Speed for 30 seconds.",
                            50,
                            sp -> Abilities.speedBoost(sp, 600, 2))));
}
'''

FILES[J + "item/ModCreativeTabs.java"] = r'''
package com.example.skyblockmod.item;

import com.example.skyblockmod.SkyblockMod;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public class ModCreativeTabs {
    public static final DeferredRegister<CreativeModeTab> TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, SkyblockMod.MODID);

    public static final DeferredHolder<CreativeModeTab, CreativeModeTab> SKYBLOCK_TAB =
            TABS.register("skyblock", () -> CreativeModeTab.builder()
                    .title(Component.translatable("itemGroup.skyblockmod"))
                    .icon(() -> new ItemStack(ModItems.ASPECT_OF_THE_END.get()))
                    .displayItems((params, output) -> {
                        // أضف هنا كل عنصر جديد ليظهر في التبويب
                        output.accept(ModItems.ASPECT_OF_THE_END.get());
                        output.accept(ModItems.ROGUE_SWORD.get());
                    })
                    .build());
}
'''

# ═══════════════ network ═══════════════

FILES[J + "network/SyncPayload.java"] = r'''
package com.example.skyblockmod.network;

import com.example.skyblockmod.SkyblockMod;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;

public record SyncPayload(double mana, double maxMana) implements CustomPacketPayload {

    public static final Type<SyncPayload> TYPE =
            new Type<>(ResourceLocation.fromNamespaceAndPath(SkyblockMod.MODID, "sync"));

    public static final StreamCodec<ByteBuf, SyncPayload> STREAM_CODEC = StreamCodec.composite(
            ByteBufCodecs.DOUBLE, SyncPayload::mana,
            ByteBufCodecs.DOUBLE, SyncPayload::maxMana,
            SyncPayload::new);

    @Override
    public Type<? extends CustomPacketPayload> type() {
        return TYPE;
    }
}
'''

FILES[J + "network/ModNetwork.java"] = r'''
package com.example.skyblockmod.network;

import com.example.skyblockmod.SkyblockMod;
import com.example.skyblockmod.client.ClientData;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.network.event.RegisterPayloadHandlersEvent;
import net.neoforged.neoforge.network.registration.PayloadRegistrar;

@EventBusSubscriber(modid = SkyblockMod.MODID, bus = EventBusSubscriber.Bus.MOD)
public class ModNetwork {

    @SubscribeEvent
    public static void register(RegisterPayloadHandlersEvent event) {
        PayloadRegistrar registrar = event.registrar("1");
        registrar.playToClient(SyncPayload.TYPE, SyncPayload.STREAM_CODEC, (payload, ctx) -> {
            ClientData.mana = payload.mana();
            ClientData.maxMana = payload.maxMana();
        });
    }
}
'''

# ═══════════════ event ═══════════════

FILES[J + "event/SkyEvents.java"] = r'''
package com.example.skyblockmod.event;

import com.example.skyblockmod.SkyblockMod;
import com.example.skyblockmod.data.ModAttachments;
import com.example.skyblockmod.data.SkyData;
import com.example.skyblockmod.network.SyncPayload;
import com.example.skyblockmod.stats.SkyStats;
import com.example.skyblockmod.stats.StatCalculator;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;
import net.neoforged.neoforge.network.PacketDistributor;

@EventBusSubscriber(modid = SkyblockMod.MODID)
public class SkyEvents {

    private static final ResourceLocation HEALTH_MOD =
            ResourceLocation.fromNamespaceAndPath(SkyblockMod.MODID, "sky_health");

    public static void sync(ServerPlayer player) {
        SkyData data = player.getData(ModAttachments.SKY_DATA);
        SkyStats stats = StatCalculator.compute(player);
        PacketDistributor.sendToPlayer(player,
                new SyncPayload(data.mana, StatCalculator.maxMana(stats)));
    }

    @SubscribeEvent
    public static void onLogin(PlayerEvent.PlayerLoggedInEvent event) {
        if (event.getEntity() instanceof ServerPlayer sp) sync(sp);
    }

    @SubscribeEvent
    public static void onRespawn(PlayerEvent.PlayerRespawnEvent event) {
        if (event.getEntity() instanceof ServerPlayer sp) sync(sp);
    }

    // كل ثانية: تجدد Mana (2% من الأقصى) + تطبيق Health
    @SubscribeEvent
    public static void onPlayerTick(PlayerTickEvent.Post event) {
        if (!(event.getEntity() instanceof ServerPlayer sp)) return;
        if (sp.tickCount % 20 != 0) return;

        SkyData data = sp.getData(ModAttachments.SKY_DATA);
        SkyStats stats = StatCalculator.compute(sp);
        int max = StatCalculator.maxMana(stats);
        data.mana = Math.min(max, data.mana + max * 0.02);

        AttributeInstance health = sp.getAttribute(Attributes.MAX_HEALTH);
        if (health != null) {
            // كل 5 Health = 1 نقطة حياة (القاعدة 100 = 20 نقطة = الحياة الطبيعية)
            health.addOrReplacePermanentModifier(new AttributeModifier(
                    HEALTH_MOD, stats.health() / 5.0 - 20.0, AttributeModifier.Operation.ADD_VALUE));
        }
        sync(sp);
    }

    // الهجوم = (5 + Damage السلاح) × (1 + Strength/100) × (1 + CritDamage/100 عند الكريت)
    // الدفاع = الضرر × 100 / (100 + Defense)
    @SubscribeEvent
    public static void onDamage(LivingIncomingDamageEvent event) {
        if (event.getSource().getEntity() instanceof ServerPlayer attacker
                && event.getSource().getDirectEntity() == attacker) {
            SkyStats s = StatCalculator.compute(attacker);
            float base = event.getAmount();
            SkyStats held = StatCalculator.statsOf(attacker.getMainHandItem());
            if (held.damage() > 0) {
                base = 5 + held.damage();
            }
            float dmg = base * (1 + s.strength() / 100f);
            if (attacker.getRandom().nextInt(100) < s.critChance()) {
                dmg *= 1 + s.critDamage() / 100f;
            }
            event.setAmount(dmg);
        }

        if (event.getEntity() instanceof ServerPlayer victim) {
            int def = StatCalculator.compute(victim).defense();
            event.setAmount(event.getAmount() * (100f / (100f + def)));
        }
    }
}
'''

FILES[J + "event/SkyCommands.java"] = r'''
package com.example.skyblockmod.event;

import com.example.skyblockmod.SkyblockMod;
import com.example.skyblockmod.data.ModAttachments;
import com.example.skyblockmod.data.SkyData;
import com.example.skyblockmod.stats.SkyStats;
import com.example.skyblockmod.stats.StatCalculator;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.RegisterCommandsEvent;

@EventBusSubscriber(modid = SkyblockMod.MODID)
public class SkyCommands {

    @SubscribeEvent
    public static void register(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("sb").executes(ctx -> {
            ServerPlayer p = ctx.getSource().getPlayerOrException();
            SkyData d = p.getData(ModAttachments.SKY_DATA);
            SkyStats s = StatCalculator.compute(p);

            send(p, "══════ SkyBlock Stats ══════", ChatFormatting.GOLD);
            send(p, "Mana: " + (int) d.mana + "/" + StatCalculator.maxMana(s), ChatFormatting.AQUA);
            send(p, "Damage: " + s.damage() + "   Strength: " + s.strength(), ChatFormatting.RED);
            send(p, "Crit Chance: " + s.critChance() + "%   Crit Damage: " + s.critDamage() + "%",
                    ChatFormatting.BLUE);
            send(p, "Health: " + s.health() + "   Defense: " + s.defense(), ChatFormatting.GREEN);
            return 1;
        }));
    }

    private static void send(ServerPlayer p, String text, ChatFormatting color) {
        p.sendSystemMessage(Component.literal(text).withStyle(color));
    }
}
'''

# ═══════════════ client ═══════════════

FILES[J + "client/ClientData.java"] = r'''
package com.example.skyblockmod.client;

public class ClientData {
    public static double mana = 100;
    public static double maxMana = 100;
}
'''

FILES[J + "client/ClientEvents.java"] = r'''
package com.example.skyblockmod.client;

import com.example.skyblockmod.SkyblockMod;
import net.minecraft.client.Minecraft;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.RegisterGuiLayersEvent;

@EventBusSubscriber(modid = SkyblockMod.MODID, bus = EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public class ClientEvents {

    @SubscribeEvent
    public static void registerLayers(RegisterGuiLayersEvent event) {
        event.registerAboveAll(
                ResourceLocation.fromNamespaceAndPath(SkyblockMod.MODID, "sky_hud"),
                (graphics, deltaTracker) -> {
                    Minecraft mc = Minecraft.getInstance();
                    if (mc.player == null || mc.options.hideGui) return;

                    int w = graphics.guiWidth();
                    int h = graphics.guiHeight();
                    String mana = (int) ClientData.mana + "/" + (int) ClientData.maxMana + " Mana";
                    graphics.drawString(mc.font, mana, w / 2 + 10, h - 60, 0x55FFFF, true);
                });
    }
}
'''

FILES[J + "client/VanillaTooltip.java"] = r'''
package com.example.skyblockmod.client;

import com.example.skyblockmod.SkyblockMod;
import com.example.skyblockmod.item.SkyItem;
import com.example.skyblockmod.stats.SkyStats;
import com.example.skyblockmod.stats.VanillaStats;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.entity.player.ItemTooltipEvent;

import java.util.List;

/** يعرض الإحصائيات على العناصر الأصلية */
@EventBusSubscriber(modid = SkyblockMod.MODID, value = Dist.CLIENT)
public class VanillaTooltip {

    @SubscribeEvent
    public static void onTooltip(ItemTooltipEvent event) {
        if (event.getItemStack().getItem() instanceof SkyItem) return;

        SkyStats s = VanillaStats.get(event.getItemStack().getItem());
        if (s.isEmpty()) return;

        List<Component> tip = event.getToolTip();
        int at = Math.min(1, tip.size());
        if (s.damage() > 0) tip.add(at++, line("Damage", s.damage(), ChatFormatting.RED));
        if (s.defense() > 0) tip.add(at++, line("Defense", s.defense(), ChatFormatting.GREEN));
        tip.add(at, Component.empty());
    }

    private static Component line(String name, int value, ChatFormatting color) {
        return Component.literal(name + ": ").withStyle(ChatFormatting.GRAY)
                .append(Component.literal("+" + value).withStyle(color));
    }
}
'''

# ═══════════════ الكتابة على القرص ═══════════════

ROOT = "skyblockmod"
for path, content in FILES.items():
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="\n") as f:
        f.write(content.lstrip("\n"))
    print("created", full)

print("\nDone! Folder:", ROOT)
