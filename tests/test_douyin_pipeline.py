import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
PIPELINE_PATH = ROOT / "scripts" / "pipeline_enhanced.py"


def load_pipeline_module():
    spec = importlib.util.spec_from_file_location("pipeline_enhanced", PIPELINE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DouyinPipelineTests(unittest.TestCase):
    def test_get_douyin_video_info_reads_title_and_author(self):
        module = load_pipeline_module()
        render_data = {
            "loaderData": {
                "video_(id)/page": {
                    "aweme_detail": {
                        "desc": "测试抖音标题",
                        "author": {"nickname": "测试作者"},
                    }
                }
            }
        }

        with mock.patch.object(
            module.DouyinDownloader,
            "get_redirect_url",
            return_value=("https://www.douyin.com/video/123", "ua", "<html></html>"),
        ), mock.patch.object(
            module.DouyinDownloader, "extract_render_data", return_value=render_data
        ):
            info = module.get_douyin_video_info("https://www.douyin.com/video/123")

        self.assertTrue(info["success"])
        self.assertEqual(info["title"], "测试抖音标题")
        self.assertEqual(info["uploader"], "测试作者")

    def test_download_step_uses_douyin_downloader_function(self):
        module = load_pipeline_module()

        with tempfile.TemporaryDirectory() as tmpdir, mock.patch.object(
            module, "get_video_info", return_value={"success": False, "title": "", "uploader": ""}
        ), mock.patch.object(
            module.DouyinDownloader, "is_douyin_url", return_value=True
        ), mock.patch.object(
            module.DouyinDownloader, "download_douyin_video"
        ) as download_mock:
            def fake_download(_url, output_path):
                Path(output_path).write_bytes(b"fake mp4 bytes")
                return True

            download_mock.side_effect = fake_download

            pipeline = module.VideoAnalysisPipeline("https://v.douyin.com/test/", tmpdir)
            pipeline._step_download_video()

            self.assertTrue(pipeline.video_path.exists())
            self.assertIn("download_video", pipeline.results["steps_completed"])


if __name__ == "__main__":
    unittest.main()
