// One-time development tool. Not part of the frontend runtime bundle.
// Copies source widget art into runtime paths and normalizes irregular
// character and plant sheets into deterministic integer-cell atlases.
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Imaging;
using System.IO;
using System.Runtime.InteropServices;

internal static class Program
{
    private const int AlphaThreshold = 16;
    private const int MrBloomColumns = 4;
    private const int MrBloomRows = 8;
    private const int MrBloomCellWidth = 288;
    private const int MrBloomCellHeight = 144;
    private const int PlantColumns = 8;
    private const int PlantRows = 2;
    private const int PlantCellWidth = 288;
    private const int PlantCellHeight = 448;
    private const int PlantBottomPad = 24;

    private static int Main(string[] args)
    {
        string root = args.Length > 0 ? args[0] : FindRepoRoot();
        string sourceDir = Path.Combine(root, "design-assets", "widget");
        string runtimeDir = Path.Combine(root, "frontend", "static", "assets", "widget");

        NormalizeMrBloomSheet(
            Path.Combine(sourceDir, "characters", "mr-bloom-spritesheet.png"),
            Path.Combine(runtimeDir, "characters", "mr-bloom-spritesheet.png"));
        CopyExact(
            Path.Combine(sourceDir, "icons", "leaf-icon.png"),
            Path.Combine(runtimeDir, "icons", "leaf-icon.png"));

        NormalizePlantSheet(
            Path.Combine(sourceDir, "plants", "monstera-spritesheet.png"),
            Path.Combine(runtimeDir, "plants", "monstera-spritesheet.png"));
        NormalizePlantSheet(
            Path.Combine(sourceDir, "plants", "sunflower-spritesheet.png"),
            Path.Combine(runtimeDir, "plants", "sunflower-spritesheet.png"));
        NormalizePlantSheet(
            Path.Combine(sourceDir, "plants", "bonsai-spritesheet.png"),
            Path.Combine(runtimeDir, "plants", "bonsai-spritesheet.png"));
        NormalizePlantSheet(
            Path.Combine(sourceDir, "plants", "jasmine-spriresheet.png"),
            Path.Combine(runtimeDir, "plants", "jasmine-spritesheet.png"));
        NormalizePlantSheet(
            Path.Combine(sourceDir, "plants", "lavender-spritesheet.png"),
            Path.Combine(runtimeDir, "plants", "lavender-spritesheet.png"));

        return 0;
    }

    private static string FindRepoRoot()
    {
        DirectoryInfo dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir != null)
        {
            if (File.Exists(Path.Combine(dir.FullName, "AGENTS.md")))
            {
                return dir.FullName;
            }

            dir = dir.Parent;
        }

        throw new InvalidOperationException("Could not find the repository root.");
    }

    private static void CopyExact(string source, string dest)
    {
        Directory.CreateDirectory(Path.GetDirectoryName(dest));
        File.Copy(source, dest, true);
        using (Image image = Image.FromFile(dest))
        {
            Console.WriteLine("copied " + dest + " (" + image.Width + "x" + image.Height + ")");
        }
    }

    private static void NormalizeMrBloomSheet(string sourcePath, string destPath)
    {
        using (Bitmap source = new Bitmap(sourcePath))
        {
            if (source.Height != MrBloomRows * MrBloomCellHeight)
            {
                throw new InvalidOperationException(
                    sourcePath + " must contain eight exact 144px rows.");
            }

            List<Rectangle> frames = new List<Rectangle>(MrBloomColumns * MrBloomRows);
            PixelBuffer pixels = LockPixels(source);
            try
            {
                for (int row = 0; row < MrBloomRows; row++)
                {
                    int y0 = row * MrBloomCellHeight;
                    int y1 = y0 + MrBloomCellHeight;
                    List<int[]> bands = MrBloomFrameBands(pixels, y0, y1);
                    if (bands.Count != MrBloomColumns)
                    {
                        throw new InvalidOperationException(
                            sourcePath + " row " + row + " produced " + bands.Count
                            + " horizontal bands, expected " + MrBloomColumns + ".");
                    }

                    for (int col = 0; col < bands.Count; col++)
                    {
                        frames.Add(OpaqueBounds(
                            pixels, bands[col][0], y0, bands[col][1], y1, 0));
                    }
                }
            }
            finally
            {
                source.UnlockBits(pixels.Data);
            }

            using (Bitmap atlas = new Bitmap(
                MrBloomColumns * MrBloomCellWidth,
                MrBloomRows * MrBloomCellHeight,
                PixelFormat.Format32bppArgb))
            {
                using (Graphics graphics = Graphics.FromImage(atlas))
                {
                    graphics.Clear(Color.Transparent);
                    graphics.CompositingMode = CompositingMode.SourceCopy;
                    graphics.InterpolationMode = InterpolationMode.NearestNeighbor;
                    graphics.PixelOffsetMode = PixelOffsetMode.Half;
                    graphics.SmoothingMode = SmoothingMode.None;

                    for (int index = 0; index < frames.Count; index++)
                    {
                        Rectangle box = frames[index];
                        int col = index % MrBloomColumns;
                        int row = index / MrBloomColumns;
                        int cellX = col * MrBloomCellWidth;
                        int cellY = row * MrBloomCellHeight;
                        int destX = cellX + (MrBloomCellWidth - box.Width) / 2;
                        int destY = cellY + MrBloomCellHeight - box.Height;
                        if (box.Width > MrBloomCellWidth || box.Height > MrBloomCellHeight)
                        {
                            throw new InvalidOperationException(
                                sourcePath + " frame " + index + " (" + box.Width + "x"
                                + box.Height + ") does not fit in a 288x144 cell.");
                        }

                        graphics.DrawImage(
                            source,
                            new Rectangle(destX, destY, box.Width, box.Height),
                            box,
                            GraphicsUnit.Pixel);
                        Console.WriteLine(
                            "Mr. Bloom row " + row + " col " + col + ": source "
                            + box.X + "," + box.Y + " " + box.Width + "x" + box.Height
                            + " -> " + destX + "," + destY);
                    }
                }

                ClearAdjacentRowBleed(atlas);

                Directory.CreateDirectory(Path.GetDirectoryName(destPath));
                atlas.Save(destPath, ImageFormat.Png);
                Console.WriteLine(
                    "normalized " + destPath + " (" + atlas.Width + "x" + atlas.Height + ")");
            }
        }
    }

    private static void ClearAdjacentRowBleed(Bitmap atlas)
    {
        // The source rows overlap: up to seven rows of the previous centered
        // robot appear at the top of the next row. The far-right 68px remain
        // untouched because later frames place their intended Z/effect art there.
        const int bleedRows = 7;
        const int centeredRobotRegionWidth = 220;
        Rectangle atlasRect = new Rectangle(0, 0, atlas.Width, atlas.Height);
        BitmapData data = atlas.LockBits(
            atlasRect,
            ImageLockMode.ReadWrite,
            PixelFormat.Format32bppArgb);
        byte[] bytes = new byte[data.Stride * atlas.Height];
        Marshal.Copy(data.Scan0, bytes, 0, bytes.Length);
        try
        {
            for (int row = 1; row < MrBloomRows; row++)
            {
                int y0 = row * MrBloomCellHeight;
                for (int col = 0; col < MrBloomColumns; col++)
                {
                    int x0 = col * MrBloomCellWidth;
                    for (int y = y0; y < y0 + bleedRows; y++)
                    {
                        for (int x = x0; x < x0 + centeredRobotRegionWidth; x++)
                        {
                            int offset = y * data.Stride + x * 4;
                            bytes[offset] = 0;
                            bytes[offset + 1] = 0;
                            bytes[offset + 2] = 0;
                            bytes[offset + 3] = 0;
                        }
                    }
                }
            }

            Marshal.Copy(bytes, 0, data.Scan0, bytes.Length);
        }
        finally
        {
            atlas.UnlockBits(data);
        }
    }

    private static void NormalizePlantSheet(string sourcePath, string destPath)
    {
        using (Bitmap source = new Bitmap(sourcePath))
        {
            PixelBuffer pixels = LockPixels(source);
            List<Rectangle> frames;
            try
            {
                List<int[]> rows = RowBands(pixels);
                if (rows.Count != PlantRows)
                {
                    throw new InvalidOperationException(
                        sourcePath + " produced " + rows.Count + " row bands, expected " + PlantRows + ".");
                }

                frames = new List<Rectangle>(16);
                frames.AddRange(FindFrameBoxes(pixels, rows[0][0], rows[0][1]));
                frames.AddRange(FindFrameBoxes(pixels, rows[1][0], rows[1][1]));
            }
            finally
            {
                source.UnlockBits(pixels.Data);
            }

            if (frames.Count != 16)
            {
                throw new InvalidOperationException(
                    sourcePath + " produced " + frames.Count + " frames, expected 16.");
            }

            using (Bitmap atlas = new Bitmap(
                    PlantColumns * PlantCellWidth,
                    PlantRows * PlantCellHeight,
                    PixelFormat.Format32bppArgb))
                {
                    using (Graphics graphics = Graphics.FromImage(atlas))
                    {
                        graphics.Clear(Color.Transparent);
                        graphics.CompositingMode = CompositingMode.SourceCopy;
                        graphics.InterpolationMode = InterpolationMode.NearestNeighbor;
                        graphics.PixelOffsetMode = PixelOffsetMode.Half;
                        graphics.SmoothingMode = SmoothingMode.None;

                        for (int index = 0; index < frames.Count; index++)
                        {
                            Rectangle box = frames[index];
                            int col = index % PlantColumns;
                            int row = index / PlantColumns;
                            int destX = col * PlantCellWidth + (PlantCellWidth - box.Width) / 2;
                            int destY = row * PlantCellHeight + PlantCellHeight - PlantBottomPad - box.Height;
                            if (destX < col * PlantCellWidth || destY < row * PlantCellHeight)
                            {
                                throw new InvalidOperationException(
                                    sourcePath + " frame " + index + " does not fit in cell.");
                            }

                            graphics.DrawImage(
                                source,
                                new Rectangle(destX, destY, box.Width, box.Height),
                                box,
                                GraphicsUnit.Pixel);
                        }
                    }

                    Directory.CreateDirectory(Path.GetDirectoryName(destPath));
                    atlas.Save(destPath, ImageFormat.Png);
                    Console.WriteLine("normalized " + destPath + " (" + atlas.Width + "x" + atlas.Height + ")");
                }
        }
    }

    private static List<Rectangle> FindFrameBoxes(PixelBuffer pixels, int y0, int y1)
    {
        List<int[]> bands = ColumnBands(pixels, y0, y1, AlphaThreshold);
        if (bands.Count != PlantColumns)
        {
            throw new InvalidOperationException(
                "Expected " + PlantColumns + " column bands in y=" + y0 + ".." + y1 + ", found " + bands.Count + ".");
        }

        List<Rectangle> boxes = new List<Rectangle>(PlantColumns);
        for (int i = 0; i < bands.Count; i++)
        {
            boxes.Add(OpaqueBounds(pixels, bands[i][0], y0, bands[i][1], y1, AlphaThreshold));
        }

        return boxes;
    }

    private static List<int[]> MrBloomFrameBands(PixelBuffer pixels, int y0, int y1)
    {
        List<int[]> occupiedRuns = ColumnBands(pixels, y0, y1, AlphaThreshold);
        if (occupiedRuns.Count < MrBloomColumns)
        {
            throw new InvalidOperationException(
                "Expected at least four occupied runs in Mr. Bloom row y=" + y0 + ".." + y1
                + ", found " + occupiedRuns.Count + ".");
        }

        // Effects such as rays and Zs can be detached from their robot, so raw
        // alpha runs are not frames. The three widest transparent gaps are the
        // stable separators between the four left-to-right sprite clusters.
        List<int[]> gaps = new List<int[]>();
        for (int index = 0; index < occupiedRuns.Count - 1; index++)
        {
            gaps.Add(new int[] {
                index,
                occupiedRuns[index + 1][0] - occupiedRuns[index][1]
            });
        }
        gaps.Sort((left, right) => {
            int byWidth = right[1].CompareTo(left[1]);
            return byWidth != 0 ? byWidth : left[0].CompareTo(right[0]);
        });

        List<int> separators = new List<int>();
        for (int index = 0; index < MrBloomColumns - 1; index++)
        {
            separators.Add(gaps[index][0]);
        }
        separators.Sort();

        List<int[]> frames = new List<int[]>(MrBloomColumns);
        int firstRun = 0;
        for (int frame = 0; frame < MrBloomColumns; frame++)
        {
            int lastRun = frame < separators.Count
                ? separators[frame]
                : occupiedRuns.Count - 1;
            frames.Add(new int[] {
                occupiedRuns[firstRun][0],
                occupiedRuns[lastRun][1]
            });
            firstRun = lastRun + 1;
        }

        return frames;
    }

    private static List<int[]> RowBands(PixelBuffer pixels)
    {
        bool[] occupied = new bool[pixels.Height];
        for (int y = 0; y < pixels.Height; y++)
        {
            for (int x = 0; x < pixels.Width; x++)
            {
                if (pixels.Alpha(x, y) > AlphaThreshold)
                {
                    occupied[y] = true;
                    break;
                }
            }
        }

        List<int[]> bands = new List<int[]>();
        int start = -1;
        for (int y = 0; y < occupied.Length; y++)
        {
            if (occupied[y] && start < 0)
            {
                start = y;
            }

            if (!occupied[y] && start >= 0)
            {
                bands.Add(new int[] { start, y });
                start = -1;
            }
        }

        if (start >= 0)
        {
            bands.Add(new int[] { start, occupied.Length });
        }

        return bands;
    }

    private static List<int[]> ColumnBands(PixelBuffer pixels, int y0, int y1, int alphaThreshold)
    {
        bool[] occupied = new bool[pixels.Width];
        for (int x = 0; x < pixels.Width; x++)
        {
            for (int y = y0; y < y1; y++)
            {
                if (pixels.Alpha(x, y) > alphaThreshold)
                {
                    occupied[x] = true;
                    break;
                }
            }
        }

        List<int[]> bands = new List<int[]>();
        int start = -1;
        for (int x = 0; x < occupied.Length; x++)
        {
            if (occupied[x] && start < 0)
            {
                start = x;
            }

            if (!occupied[x] && start >= 0)
            {
                bands.Add(new int[] { start, x });
                start = -1;
            }
        }

        if (start >= 0)
        {
            bands.Add(new int[] { start, occupied.Length });
        }

        return bands;
    }

    private static Rectangle OpaqueBounds(
        PixelBuffer pixels, int x0, int y0, int x1, int y1, int alphaThreshold)
    {
        int minX = x1;
        int minY = y1;
        int maxX = x0 - 1;
        int maxY = y0 - 1;
        for (int y = y0; y < y1; y++)
        {
            for (int x = x0; x < x1; x++)
            {
                if (pixels.Alpha(x, y) <= alphaThreshold)
                {
                    continue;
                }

                if (x < minX) minX = x;
                if (x > maxX) maxX = x;
                if (y < minY) minY = y;
                if (y > maxY) maxY = y;
            }
        }

        if (maxX < minX)
        {
            throw new InvalidOperationException("Empty frame in " + x0 + "," + y0 + "-" + x1 + "," + y1 + ".");
        }

        return Rectangle.FromLTRB(minX, minY, maxX + 1, maxY + 1);
    }

    private static PixelBuffer LockPixels(Bitmap bitmap)
    {
        BitmapData data = bitmap.LockBits(
            new Rectangle(0, 0, bitmap.Width, bitmap.Height),
            ImageLockMode.ReadOnly,
            PixelFormat.Format32bppArgb);
        byte[] bytes = new byte[data.Stride * bitmap.Height];
        Marshal.Copy(data.Scan0, bytes, 0, bytes.Length);
        return new PixelBuffer(bitmap.Width, bitmap.Height, data, bytes);
    }

    private sealed class PixelBuffer
    {
        public PixelBuffer(int width, int height, BitmapData data, byte[] bytes)
        {
            Width = width;
            Height = height;
            Data = data;
            Bytes = bytes;
        }

        public int Width;
        public int Height;
        public BitmapData Data;
        public byte[] Bytes;

        public byte Alpha(int x, int y)
        {
            return Bytes[y * Data.Stride + x * 4 + 3];
        }
    }
}
