"""empty message

Revision ID: ea8265a5126e
Revises: 
Create Date: 2021-05-02 16:54:47.848845

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea8265a5126e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Artist',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(), nullable=True),
                    sa.Column('city', sa.String(length=120), nullable=True),
                    sa.Column('state', sa.String(length=120), nullable=True),
                    sa.Column('phone', sa.String(length=120), nullable=True),
                    sa.Column('genres', sa.String(length=120), nullable=True),
                    sa.Column('image_link', sa.String(
                        length=500), nullable=True),
                    sa.Column('facebook_link', sa.String(
                        length=120), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('Venue',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(), nullable=True),
                    sa.Column('city', sa.String(length=120), nullable=True),
                    sa.Column('state', sa.String(length=120), nullable=True),
                    sa.Column('address', sa.String(length=120), nullable=True),
                    sa.Column('phone', sa.String(length=120), nullable=True),
                    sa.Column('image_link', sa.String(
                        length=500), nullable=True),
                    sa.Column('facebook_link', sa.String(
                        length=120), nullable=True),
                    sa.Column('genres', sa.ARRAY(sa.String()), nullable=False),
                    sa.Column('website', sa.String(length=250), nullable=True),
                    sa.Column('seeking_talent', sa.Boolean(), nullable=True),
                    sa.Column('seeking_description', sa.String(
                        length=250), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Venue')
    op.drop_table('Artist')
    # ### end Alembic commands ###
