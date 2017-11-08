# coding=utf-8
from __future__ import absolute_import

import shutil
import time
import yaml
import click
from tempfile import NamedTemporaryFile as tempfile
from gcodeInterpreter import gcode


@click.command()
@click.option("--speed-x", "speedx", type=float, default=6000)
@click.option("--speed-y", "speedy", type=float, default=6000)
@click.option("--speed-z", "speedz", type=float, default=300)
@click.option("--offset", "offset", type=(float, float), multiple=True)
@click.option("--max-t", "maxt", type=int, default=10)
@click.option("--g90-extruder", "g90_extruder", is_flag=True)
@click.option("--progress", "progress", is_flag=True)
@click.argument("path", type=click.Path(exists=True))
def gcode_analysis(path, speedx, speedy, speedz, offset, maxt, g90_extruder, progress):
    offsets = offset
    if offsets is None:
        offsets = []
    elif isinstance(offset, tuple):
        offsets = list(offsets)
    offsets = [(0, 0)] + offsets
    if len(offsets) < maxt:
        offsets += [(0, 0)] * (maxt - len(offsets))

    start_time = time.time()

    progress_callback = None
    if progress:
        def progress_callback(percentage):
            click.echo("PROGRESS:{}".format(percentage))

    interpreter = gcode(progress_callback=progress_callback)

    interpreter.load(path,
                     speedx=speedx,
                     speedy=speedy,
                     offsets=offsets,
                     max_extruders=maxt,
                     g90_extruder=g90_extruder)

    ystr = yaml.safe_dump(interpreter.get_result(), default_flow_style=False, indent="    ", allow_unicode=True)

    with open(path, "r") as src_file, tempfile("w", delete=False) as dst_file:
        dst_file.write(";OCTOPRINT_METADATA\n")
        for line in ystr.splitlines():
            dst_file.write(";{}\n".format(line))
        dst_file.write(";OCTOPRINT_METADATA_END\n")
        dst_file.write("\n")
        dst_file.write(src_file.read())

    shutil.move(dst_file.name, path)

    click.echo("DONE:{}s".format(time.time() - start_time))


if __name__ == "__main__":
    gcode_analysis()